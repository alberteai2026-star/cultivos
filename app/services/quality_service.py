from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.quality_repository import QualityRepository
from app.repositories.user_farm_role_repository import UserFarmRoleRepository
from app.schemas.quality import QualityTestListResponse


class QualityService:
    def __init__(self, db: Session):
        self.db = db
        self.quality = QualityRepository(db)
        self.relations = UserFarmRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_tests_for_user(
        self,
        user: User,
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        test_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> QualityTestListResponse:
        farm_ids = self.relations.list_farm_ids_by_user(user.id)
        if farm_id is not None and farm_id not in farm_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        total, items = self.quality.list_tests_by_farm_ids(
            farm_ids,
            farm_id=farm_id,
            plot_id=plot_id,
            status_value=status_value,
            test_type=test_type,
            limit=limit,
            offset=offset,
        )
        return QualityTestListResponse(total=total, items=items)

    def create_test_for_user(self, *, user: User, farm_id: int, plot_id: int | None, harvest_id: int | None, test_type: str, result_value: str, status_value: str, tested_at):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        test = self.quality.create_test(farm_id=farm_id, plot_id=plot_id, harvest_id=harvest_id, test_type=test_type, result_value=result_value, status=status_value, tested_at=tested_at)
        self.audit.add(module='quality', action='create_test', user_id=user.id, farm_id=farm_id, record_id=str(test.id))
        self.db.commit(); self.db.refresh(test)
        return test

    def get_test_for_user(self, *, user: User, test_id: int):
        test = self.quality.get_test_by_id(test_id)
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prueba de calidad no encontrada')
        if not self.relations.user_has_farm(user_id=user.id, farm_id=test.farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        return test

    def update_test_for_user(self, *, user: User, test_id: int, result_value: str | None, status_value: str | None, tested_at):
        test = self.get_test_for_user(user=user, test_id=test_id)
        updated = self.quality.update_test_fields(test, result_value=result_value, status=status_value, tested_at=tested_at)
        self.audit.add(module='quality', action='update_test', user_id=user.id, farm_id=test.farm_id, record_id=str(test.id))
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def list_certifications_for_user(self, user: User):
        return self.quality.list_certifications_by_farm_ids(self.relations.list_farm_ids_by_user(user.id))

    def create_certification_for_user(self, *, user: User, farm_id: int, name: str, issuer: str | None, valid_until):
        if not self.relations.user_has_farm(user_id=user.id, farm_id=farm_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tienes acceso a esta finca')
        cert = self.quality.create_certification(farm_id=farm_id, name=name, issuer=issuer, valid_until=valid_until)
        self.audit.add(module='quality', action='create_certification', user_id=user.id, farm_id=farm_id, record_id=str(cert.id))
        self.db.commit(); self.db.refresh(cert)
        return cert
