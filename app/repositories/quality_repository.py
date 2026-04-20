from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.certification import Certification
from app.models.quality_test import QualityTest


class QualityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_test(
        self,
        *,
        farm_id: int,
        plot_id: int | None,
        harvest_id: int | None,
        test_type: str,
        result_value: str,
        status: str,
        tested_at,
    ) -> QualityTest:
        test = QualityTest(
            farm_id=farm_id,
            plot_id=plot_id,
            harvest_id=harvest_id,
            test_type=test_type,
            result_value=result_value,
            status=status,
            tested_at=tested_at,
        )
        self.db.add(test)
        self.db.flush()
        return test

    def list_tests_by_farm_ids(self, farm_ids: list[int]) -> list[QualityTest]:
        if not farm_ids:
            return []
        q = select(QualityTest).where(QualityTest.farm_id.in_(farm_ids)).order_by(QualityTest.id.desc())
        return list(self.db.scalars(q).all())

    def create_certification(self, *, farm_id: int, name: str, issuer: str | None, valid_until) -> Certification:
        cert = Certification(farm_id=farm_id, name=name, issuer=issuer, valid_until=valid_until, status='vigente')
        self.db.add(cert)
        self.db.flush()
        return cert

    def list_certifications_by_farm_ids(self, farm_ids: list[int]) -> list[Certification]:
        if not farm_ids:
            return []
        q = select(Certification).where(Certification.farm_id.in_(farm_ids)).order_by(Certification.id.desc())
        return list(self.db.scalars(q).all())
