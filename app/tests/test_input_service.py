from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.services.input_service import InputService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _RelationsAllow:
    def list_farm_ids_by_user(self, user_id: int):
        return [10, 20]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return farm_id in {10, 20}


class _RelationsDeny:
    def list_farm_ids_by_user(self, user_id: int):
        return []

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return False


class _Product:
    def __init__(self):
        self.id = 2
        self.name = 'Urea'


class _Application:
    def __init__(self):
        self.id = 5
        self.farm_id = 10
        self.quantity = 1.0
        self.unit = 'kg'


class _InputsRepo:
    def __init__(self):
        self.last_args = None
        self.product = _Product()
        self.application = _Application()

    def list_products(self, **kwargs):
        self.last_args = kwargs
        return 1, [self.product]

    def get_product_by_id(self, product_id: int):
        return self.product if product_id == self.product.id else None

    def update_product_fields(self, product, **kwargs):
        self.last_args = kwargs
        return product

    def list_applications_by_farm_ids(self, farm_ids, **kwargs):
        self.last_args = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.application]

    def get_application_by_id(self, application_id: int):
        return self.application if application_id == self.application.id else None

    def update_application_fields(self, app, **kwargs):
        self.last_args = kwargs
        for key, value in kwargs.items():
            if value is not None:
                setattr(app, key, value)
        return app


class _AuditRepo:
    def __init__(self):
        self.entries = []

    def add(self, **kwargs):
        self.entries.append(kwargs)


class _DB:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1

    def refresh(self, _obj):
        return None


def test_list_products_forwards_filters_and_pagination():
    service = InputService(db=None)
    repo = _InputsRepo()
    service.inputs = repo

    payload = service.list_products(search='ur', category='fertilizante', limit=50, offset=5)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert repo.last_args == {'search': 'ur', 'category': 'fertilizante', 'limit': 50, 'offset': 5}


def test_list_applications_rejects_invalid_date_range():
    service = InputService(db=None)
    service.inputs = _InputsRepo()
    service.relations = _RelationsAllow()

    start = datetime.utcnow()
    end = start - timedelta(days=1)

    with pytest.raises(HTTPException) as exc:
        service.list_applications_for_user(_User(1), applied_from=start, applied_to=end)

    assert exc.value.status_code == 422


def test_get_application_for_user_denies_access_without_farm_relation():
    service = InputService(db=None)
    service.inputs = _InputsRepo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_application_for_user(user=_User(1), application_id=5)

    assert exc.value.status_code == 403


def test_update_application_for_user_updates_and_audits():
    db = _DB()
    service = InputService(db=db)
    service.inputs = _InputsRepo()
    service.relations = _RelationsAllow()
    service.audit = _AuditRepo()

    updated = service.update_application_for_user(
        user=_User(1),
        application_id=5,
        applied_at=None,
        quantity=4.5,
        unit='L',
    )

    assert updated.quantity == 4.5
    assert updated.unit == 'L'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_application'
