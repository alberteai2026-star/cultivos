from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api import deps


def _credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


class DummyDB:
    def __init__(self, user=None):
        self._user = user

    def get(self, model, user_id):
        return self._user


def test_get_current_user_success(monkeypatch):
    user = SimpleNamespace(id=1, is_active=True)
    monkeypatch.setattr(deps, "decode_access_token", lambda _: {"sub": "1"})

    current = deps.get_current_user(_credentials("ok"), DummyDB(user=user))

    assert current is user


def test_get_current_user_invalid_subject(monkeypatch):
    monkeypatch.setattr(deps, "decode_access_token", lambda _: {"sub": "abc"})

    with pytest.raises(HTTPException) as exc:
        deps.get_current_user(_credentials("bad"), DummyDB(user=None))

    assert exc.value.status_code == 401


def test_get_current_user_inactive_user(monkeypatch):
    user = SimpleNamespace(id=2, is_active=False)
    monkeypatch.setattr(deps, "decode_access_token", lambda _: {"sub": "2"})

    with pytest.raises(HTTPException) as exc:
        deps.get_current_user(_credentials("ok"), DummyDB(user=user))

    assert exc.value.status_code == 403
