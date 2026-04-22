from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.certification import Certification
from app.models.quality_record import QualityTest


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

    def list_tests_by_farm_ids(
        self,
        farm_ids: list[int],
        *,
        farm_id: int | None = None,
        plot_id: int | None = None,
        status_value: str | None = None,
        test_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[int, list[QualityTest]]:
        if not farm_ids:
            return 0, []
        q = select(QualityTest).where(QualityTest.farm_id.in_(farm_ids))
        count_q = select(func.count(QualityTest.id)).where(QualityTest.farm_id.in_(farm_ids))
        if farm_id is not None:
            q = q.where(QualityTest.farm_id == farm_id)
            count_q = count_q.where(QualityTest.farm_id == farm_id)
        if plot_id is not None:
            q = q.where(QualityTest.plot_id == plot_id)
            count_q = count_q.where(QualityTest.plot_id == plot_id)
        if status_value is not None:
            q = q.where(QualityTest.status == status_value)
            count_q = count_q.where(QualityTest.status == status_value)
        if test_type is not None:
            q = q.where(QualityTest.test_type == test_type)
            count_q = count_q.where(QualityTest.test_type == test_type)
        total = int(self.db.scalar(count_q) or 0)
        q = q.order_by(QualityTest.id.desc()).limit(limit).offset(offset)
        return total, list(self.db.scalars(q).all())

    def get_test_by_id(self, test_id: int) -> QualityTest | None:
        return self.db.get(QualityTest, test_id)

    def update_test_fields(
        self,
        test: QualityTest,
        *,
        result_value: str | None = None,
        status: str | None = None,
        tested_at=None,
    ) -> QualityTest:
        if result_value is not None:
            test.result_value = result_value
        if status is not None:
            test.status = status
        if tested_at is not None:
            test.tested_at = tested_at
        self.db.add(test)
        return test

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
