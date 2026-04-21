from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.ai_service import AIService


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


class _Insight:
    def __init__(self):
        self.id = 5
        self.farm_id = 10
        self.title = 'Riesgo hídrico'
        self.recommendation = 'Aplicar riego por goteo'
        self.predicted_value = 23.4
        self.confidence = 87.0
        self.priority = 'alta'
        self.status = 'nuevo'
        self.outcome_notes = None
        self.resolved_at = None
        self.plot_id = None
        self.crop_cycle_id = None
        self.insight_type = 'risk_alert'
        self.generated_at = datetime.utcnow()
        self.created_at = datetime.utcnow()


class _Repo:
    def __init__(self):
        self.insight = _Insight()
        self.last_kwargs = None

    def list_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.insight]

    def get_by_id(self, insight_id: int):
        return self.insight if insight_id == self.insight.id else None

    def update_fields(self, insight, **kwargs):
        self.last_kwargs = kwargs
        if kwargs.get('priority') is not None:
            insight.priority = kwargs['priority']
        return insight

    def update_status(self, insight, *, status: str, outcome_notes: str | None, resolved_at: datetime | None):
        self.last_kwargs = {'status': status, 'outcome_notes': outcome_notes, 'resolved_at': resolved_at}
        insight.status = status
        insight.outcome_notes = outcome_notes
        insight.resolved_at = resolved_at
        return insight


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


def test_list_for_user_forwards_filters_and_returns_response_shape():
    service = AIService(db=None)
    repo = _Repo()
    service.ai = repo
    service.relations = _RelationsAllow()

    response = service.list_for_user(
        _User(1),
        farm_id=10,
        insight_type='risk_alert',
        priority='alta',
        confidence_min=70,
        confidence_max=95,
        limit=20,
        offset=2,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'insight_type': 'risk_alert',
        'priority': 'alta',
        'confidence_min': 70,
        'confidence_max': 95,
        'limit': 20,
        'offset': 2,
    }


def test_get_for_user_denies_without_farm_access():
    service = AIService(db=None)
    service.ai = _Repo()
    service.relations = _RelationsDeny()

    with pytest.raises(HTTPException) as exc:
        service.get_for_user(user=_User(1), insight_id=5)

    assert exc.value.status_code == 403


def test_update_for_user_updates_and_audits():
    db = _DB()
    service = AIService(db=db)
    repo = _Repo()
    service.ai = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_for_user(
        user=_User(1),
        insight_id=5,
        title=None,
        recommendation=None,
        predicted_value=None,
        confidence=None,
        priority='media',
    )

    assert updated.priority == 'media'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_insight'


def test_update_status_for_user_updates_and_audits():
    db = _DB()
    service = AIService(db=db)
    repo = _Repo()
    service.ai = repo
    service.relations = _RelationsAllow()
    service.audit = _Audit()

    updated = service.update_status_for_user(
        user=_User(1),
        insight_id=5,
        status_value='en_revision',
        outcome_notes='Requiere validación en campo',
        resolved_at=None,
    )

    assert updated.status == 'en_revision'
    assert updated.outcome_notes == 'Requiere validación en campo'
    assert db.commits == 1
    assert len(service.audit.entries) == 1
    assert service.audit.entries[0]['action'] == 'update_insight_status'


def test_update_status_for_user_rejects_invalid_transition():
    db = _DB()
    service = AIService(db=db)
    repo = _Repo()
    repo.insight.status = 'nuevo'
    service.ai = repo
    service.relations = _RelationsAllow()

    with pytest.raises(HTTPException) as exc:
        service.update_status_for_user(
            user=_User(1),
            insight_id=5,
            status_value='validado',
            outcome_notes=None,
            resolved_at=None,
        )

    assert exc.value.status_code == 409
