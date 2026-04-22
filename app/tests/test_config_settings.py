from app.core.config import Settings


def test_cors_origins_all():
    s = Settings(cors_allow_origins="*")
    assert s.cors_origins == ["*"]


def test_cors_origins_csv_parse():
    s = Settings(cors_allow_origins="https://a.com, https://b.com")
    assert s.cors_origins == ["https://a.com", "https://b.com"]
