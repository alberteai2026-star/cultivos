import pytest
from fastapi import HTTPException

from app.services.gis_service import GISService


class _User:
    def __init__(self, user_id: int):
        self.id = user_id


class _RelationsAllow:
    def list_farm_ids_by_user(self, user_id: int):
        return [10]

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return farm_id == 10


class _RelationsDeny:
    def list_farm_ids_by_user(self, user_id: int):
        return []

    def user_has_farm(self, *, user_id: int, farm_id: int) -> bool:
        return False


class _Feature:
    def __init__(self):
        self.id = 11
        self.farm_id = 10
        self.plot_id = 2
        self.feature_type = 'polygon'
        self.name = 'Bloque A'
        self.geometry_geojson = '{"type":"Polygon"}'
        self.properties_json = '{"crop":"palma"}'
        self.created_at = '2026-01-01T00:00:00'


class _Version:
    def __init__(self):
        self.id = 33
        self.feature_id = 11
        self.version_no = 2
        self.name = 'Bloque A-1'
        self.geometry_geojson = '{"type":"Polygon"}'
        self.properties_json = '{"crop":"palma"}'
        self.changed_by_user_id = 1
        self.changed_at = '2026-01-02T00:00:00'


class _Repo:
    def __init__(self):
        self.feature = _Feature()
        self.version = _Version()
        self.last_kwargs = None

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.feature]

    def get_by_id(self, feature_id: int):
        return self.feature if feature_id == self.feature.id else None

    def update_fields(self, feature, **kwargs):
        self.last_kwargs = kwargs
        if kwargs.get('name') is not None:
            feature.name = kwargs['name']
        return feature

    def create_version(self, *, feature, changed_by_user_id: int | None):
        self.last_kwargs = {'feature_id': feature.id, 'changed_by_user_id': changed_by_user_id}
        return self.version

    def list_versions(self, feature_id: int, *, limit: int = 100, offset: int = 0):
        self.last_kwargs = {'feature_id': feature_id, 'limit': limit, 'offset': offset}
        return 1, [self.version]


class _Audit:
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


def test_list_for_user_forwards_filters_and_pagination():
    service = GISService(db=None)
    repo = _Repo()
    service.gis = repo
    service.relations = _RelationsAllow()

    response = service.list_for_user(
        _User(1),
        farm_id=10,
        plot_id=2,
        feature_type='polygon',
        name_search='Bloque',
        limit=20,
        offset=3,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'plot_id': 2,
        'feature_type': 'polygon',
        'name_search': 'Bloque',
        'limit': 20,
        'offset': 3,
    }


def test_get_for_user_denies_without_access():
    service = GISService(db=None)
    service.gis = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), feature_id=11)

    assert exc.value.status_code == 403


def test_update_for_user_updates_and_audits_and_versions():
    db = _DB()
    service = GISService(db=db)
    repo = _Repo()
    service.gis = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_for_user(
        user=_User(1),
        feature_id=11,
        name='Bloque A-1',
        geometry_geojson=None,
        properties_json=None,
    )

    assert updated.name == 'Bloque A-1'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_feature'
    assert repo.last_kwargs == {'feature_id': 11, 'changed_by_user_id': 1}


def test_list_history_for_user_returns_versions():
    service = GISService(db=None)
    repo = _Repo()
    service.gis = repo
    service.relations = _RelationsAllow()

    payload = service.list_history_for_user(user=_User(1), feature_id=11, limit=10, offset=2)

    assert payload.total == 1
    assert len(payload.items) == 1
    assert payload.items[0].version_no == 2
    assert repo.last_kwargs == {'feature_id': 11, 'limit': 10, 'offset': 2}
