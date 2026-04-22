from fastapi import Response
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1 import health as health_module


def test_health_endpoint_returns_ok_payload():
    payload = health_module.health()

    assert payload.status == 'ok'
    assert payload.service
    assert payload.timestamp is not None


def test_health_legacy_alias_returns_same_payload_shape():
    payload = health_module.health_legacy()

    assert payload.status == 'ok'
    assert payload.service
    assert payload.timestamp is not None


def test_readiness_returns_503_when_db_down(monkeypatch):
    monkeypatch.setattr(health_module, '_database_is_ready', lambda: False)

    response = Response()
    payload = health_module.readiness(response)

    assert response.status_code == 503
    assert payload.status == 'degraded'
    assert payload.database == 'down'


def test_readiness_returns_ok_when_db_up(monkeypatch):
    monkeypatch.setattr(health_module, '_database_is_ready', lambda: True)

    response = Response()
    payload = health_module.readiness(response)

    assert response.status_code == 200
    assert payload.status == 'ok'
    assert payload.database == 'up'


def test_database_is_ready_returns_true_when_query_passes(monkeypatch):
    class _DB:
        def execute(self, _query):
            return 1

        def close(self):
            return None

    monkeypatch.setattr(health_module, 'SessionLocal', lambda: _DB())

    assert health_module._database_is_ready() is True


def test_database_is_ready_returns_false_on_sqlalchemy_error(monkeypatch):
    class _DB:
        def execute(self, _query):
            raise SQLAlchemyError('db down')

        def close(self):
            return None

    monkeypatch.setattr(health_module, 'SessionLocal', lambda: _DB())

    assert health_module._database_is_ready() is False
