from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.settings_service import SettingsService


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


class _Setting:
    def __init__(self):
        now = datetime.utcnow()
        self.id = 4
        self.farm_id = 10
        self.category = 'ui'
        self.setting_key = 'language'
        self.setting_value = 'es'
        self.created_at = now
        self.updated_at = now


class _HistoryEvent:
    def __init__(self):
        self.id = 8
        self.setting_id = 4
        self.changed_by_user_id = 1
        self.previous_value = 'es'
        self.new_value = 'en'
        self.created_at = datetime.utcnow()




class _Template:
    def __init__(self):
        self.id = 1
        self.crop_type = 'cafe'
        self.category = 'riego'
        self.setting_key = 'frecuencia_dias'
        self.default_value = '7'

class _Repo:
    def __init__(self):
        self.setting = _Setting()
        self.last_kwargs = None
        self.history_events = []
        self.templates = [_Template()]

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.setting]

    def get_by_id(self, setting_id: int):
        return self.setting if setting_id == self.setting.id else None

    def get_by_unique_key(self, *, farm_id: int, category: str, setting_key: str):
        if farm_id == 10 and category == self.setting.category and setting_key == self.setting.setting_key:
            return self.setting
        return None

    def upsert_setting(self, **kwargs):
        self.setting.setting_value = kwargs['setting_value']
        return self.setting

    def add_history(self, **kwargs):
        self.history_events.append(kwargs)
        return _HistoryEvent()

    def list_history_by_setting_id(self, setting_id: int, *, limit: int = 100, offset: int = 0):
        return 1, [_HistoryEvent()] if setting_id == self.setting.id else (0, [])

    def list_templates(self, *, crop_type: str | None = None):
        if crop_type is None:
            return self.templates
        return [x for x in self.templates if x.crop_type == crop_type]


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
    service = SettingsService(db=None)
    repo = _Repo()
    service.settings = repo
    service.relations = _RelationsAllow()

    response = service.list_for_user(
        _User(1),
        farm_id=10,
        category='ui',
        setting_key_search='lang',
        limit=20,
        offset=3,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'category': 'ui',
        'setting_key_search': 'lang',
        'limit': 20,
        'offset': 3,
    }


def test_get_for_user_denies_without_access():
    service = SettingsService(db=None)
    service.settings = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), setting_id=4)

    assert exc.value.status_code == 403


def test_update_value_for_user_updates_and_audits_and_history():
    db = _DB()
    service = SettingsService(db=db)
    repo = _Repo()
    service.settings = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_value_for_user(user=_User(1), setting_id=4, setting_value='en')

    assert updated.setting_value == 'en'
    assert db.commits == 1
    assert len(repo.history_events) == 1
    assert repo.history_events[0]['previous_value'] == 'es'
    assert repo.history_events[0]['new_value'] == 'en'
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_value'


def test_list_history_for_user_returns_paged_payload():
    service = SettingsService(db=None)
    service.settings = _Repo()
    service.relations = _RelationsAllow()

    response = service.list_history_for_user(user=_User(1), setting_id=4, limit=10, offset=0)

    assert response.total == 1
    assert len(response.items) == 1
    assert response.items[0].new_value == 'en'


def test_list_templates_for_user_returns_templates():
    service = SettingsService(db=None)
    service.settings = _Repo()

    response = service.list_templates_for_user(user=_User(1), crop_type='cafe')

    assert response.total == 1
    assert response.items[0].setting_key == 'frecuencia_dias'


def test_apply_template_for_user_applies_settings_and_history():
    db = _DB()
    service = SettingsService(db=db)
    repo = _Repo()
    service.settings = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    result = service.apply_template_for_user(user=_User(1), farm_id=10, crop_type='cafe')

    assert result.applied_count == 1
    assert db.commits == 1
    assert len(repo.history_events) == 1
    assert repo.history_events[0]['new_value'] == '7'
    assert service.audit.entries[0]['action'] == 'apply_template'
