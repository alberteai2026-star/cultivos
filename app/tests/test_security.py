from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_and_verify():
    plain = "MiPassword123"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)


def test_create_and_decode_token():
    token = create_access_token(subject="99", expires_minutes=5)
    payload = decode_access_token(token)
    assert payload["sub"] == "99"
    assert "exp" in payload
