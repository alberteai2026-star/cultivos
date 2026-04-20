from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.farm_repository import FarmRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository


class FarmService:
    def __init__(self, db: Session):
        self.db = db
        self.farms = FarmRepository(db)
        self.roles = RoleRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_for_user(self, user: User):
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        return self.farms.list_by_ids(farm_ids)

    def create_for_owner(
        self,
        *,
        user: User,
        name: str,
        total_area_ha: float | None,
        department: str | None,
        municipality: str | None,
    ):
        owner_role = self.roles.get_by_code("dueno")
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
            module="farms",
            action="create",
            user_id=user.id,
            farm_id=farm.id,
            record_id=str(farm.id),
            metadata={"name": farm.name},
        )

        self.db.commit()
        self.db.refresh(farm)
        return farm
