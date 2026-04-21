from app.schemas.health import HealthOut


def test_health_schema_fields():
    payload = HealthOut(
        status="ok",
        service="Cultivos API",
        version="0.1.0",
        environment="test",
        timestamp="2026-01-01T00:00:00Z",
    )
    assert payload.status == "ok"
    assert payload.environment == "test"
