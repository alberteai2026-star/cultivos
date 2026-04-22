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

    def list_recommendations_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.insight]

    def summary_by_dimensions(self, *, farm_ids, farm_id=None):
        self.last_kwargs = {'farm_ids': farm_ids, 'farm_id': farm_id}
        return [('risk_alert', 'nuevo', 'alta', 3)]

    def harvest_history_by_plot(self, *, farm_ids, farm_id=None, lookback_limit=24):
        self.last_kwargs = {'farm_ids': farm_ids, 'farm_id': farm_id, 'lookback_limit': lookback_limit}
        return [(10, 101, 1000.0, 4, datetime(2026, 1, 2))]

    def latest_yield_insights_by_plot(self, *, farm_ids, farm_id=None):
        self.last_kwargs = {'farm_ids': farm_ids, 'farm_id': farm_id}
        forecast = _Insight()
        forecast.plot_id = 101
        forecast.insight_type = 'yield_forecast'
        forecast.predicted_value = 1200.0
        forecast.confidence = 80.0
        return {101: forecast}

    def list_predictive_alerts_by_farm_ids(self, farm_ids, **kwargs):
        self.last_kwargs = {'farm_ids': farm_ids, **kwargs}
        return 1, [self.insight]

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


def test_recommendations_for_user_returns_pending_recommendations():
    service = AIService(db=None)
    repo = _Repo()
    service.ai = repo
    service.relations = _RelationsAllow()

    response = service.recommendations_for_user(
        user=_User(1),
        farm_id=10,
        min_confidence=65,
        only_pending=True,
        limit=25,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'min_confidence': 65,
        'only_pending': True,
        'limit': 25,
    }


def test_summary_for_user_returns_grouped_dimensions():
    service = AIService(db=None)
    repo = _Repo()
    service.ai = repo
    service.relations = _RelationsAllow()

    response = service.summary_for_user(user=_User(1), farm_id=10)

    assert response.total_groups == 1
    assert response.items[0].insight_type == 'risk_alert'
    assert response.items[0].status == 'nuevo'
    assert response.items[0].priority == 'alta'
    assert response.items[0].total == 3


def test_yield_forecast_for_user_blends_historical_and_ai_values():
    service = AIService(db=None)
    repo = _Repo()
    service.ai = repo
    service.relations = _RelationsAllow()

    response = service.yield_forecast_for_user(user=_User(1), farm_id=10, lookback_limit=12)

    assert response.total == 1
    row = response.items[0]
    assert row.plot_id == 101
    assert row.historical_avg_quantity == 1000.0
    assert row.ai_predicted_quantity == 1200.0
    assert row.ai_confidence == 80.0
    assert row.projected_quantity == 1160.0


def test_predictive_alerts_for_user_filters_by_confidence():
    service = AIService(db=None)
    repo = _Repo()
    service.ai = repo
    service.relations = _RelationsAllow()

    response = service.predictive_alerts_for_user(
        user=_User(1),
        farm_id=10,
        min_confidence=75,
        limit=15,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert repo.last_kwargs == {
        'farm_ids': [10],
        'farm_id': 10,
        'min_confidence': 75,
        'limit': 15,
    }
