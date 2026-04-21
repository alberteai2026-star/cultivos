from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.farm_repository import FarmRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.farm import FarmListResponse


class FarmService:
    def __init__(self, db: Session):
        self.db = db
        self.farms = FarmRepository(db)
        self.roles = RoleRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User, *, search: str | None = None, limit: int = 100, offset: int = 0) -> FarmListResponse:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro limit debe estar entre 1 y 500')
        if offset < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='El parámetro offset debe ser mayor o igual a 0')

        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        total, items = self.farms.list_by_ids(farm_ids, search=search, limit=limit, offset=offset)
        return FarmListResponse(total=total, items=items)

    def get_for_user(self, *, user: User, farm_id: int):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        farm = self.farms.get_by_id(farm_id)
        if farm is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Finca no encontrada')
        return farm

    def create_for_owner(
        self,
        *,
        user: User,
        name: str,
        total_area_ha: float | None,
        department: str | None,
        municipality: str | None,
    ):
        owner_role = self.roles.get_by_code('dueno')
        if not owner_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Rol 'dueno' no configurado en la base de datos",
            )

        farm = self.farms.create(
            name=name,
            total_area_ha=total_area_ha,
            department=department,
            municipality=municipality,
        )

        self.relations.assign_role(user_id=user.id, farm_id=farm.id, role_id=owner_role.id)

        self.audit.add(
            module='farms',
            action='create',
            user_id=user.id,
            farm_id=farm.id,
            record_id=str(farm.id),
            metadata={'name': farm.name},
        )

        self.db.commit()
        self.db.refresh(farm)
        return farm

    def update_for_user(
        self,
        *,
        user: User,
        farm_id: int,
        name: str | None,
        total_area_ha: float | None,
        department: str | None,
        municipality: str | None,
    ):
        farm = self.farms.get_by_id(farm_id)
        if farm is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Finca no encontrada')

        owner_role = self.roles.get_by_code('dueno')
        if not owner_role:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Rol 'dueno' no configurado")

        if not self.relations.user_has_role_for_farm(user_id=user.id, farm_id=farm_id, role_id=owner_role.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Solo el dueño puede editar esta finca')

        updated = self.farms.update(
            farm,
            name=name,
            total_area_ha=total_area_ha,
            department=department,
            municipality=municipality,
        )
        self.audit.add(
            module='farms',
            action='update',
            user_id=user.id,
            farm_id=farm_id,
            record_id=str(farm_id),
            metadata={'name': updated.name},
        )
        self.db.commit()
        self.db.refresh(updated)
        return updated
