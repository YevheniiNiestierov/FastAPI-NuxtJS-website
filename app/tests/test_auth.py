"""
Unit tests for app/auth/jwt.py — token creation and verification.
"""
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth.jwt import (
    create_access_token,
    verify_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.auth.schemas import TokenData


# ── create_access_token ───────────────────────────────────────────────────────

def test_create_access_token_is_a_string():
    token = create_access_token({"sub": "user@test.com", "is_admin": False})
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_payload_contains_sub():
    token = create_access_token({"sub": "user@test.com", "is_admin": False})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "user@test.com"


def test_create_access_token_payload_contains_is_admin():
    token = create_access_token({"sub": "admin@test.com", "is_admin": True})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["is_admin"] is True


def test_create_access_token_has_expiry_claim():
    token = create_access_token({"sub": "user@test.com", "is_admin": False})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload


def test_create_access_token_expiry_is_in_future():
    token = create_access_token({"sub": "user@test.com", "is_admin": False})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp = payload["exp"]
    now = datetime.now(timezone.utc).timestamp()
    # expiry should be roughly ACCESS_TOKEN_EXPIRE_MINUTES from now
    assert exp > now
    assert exp <= now + ACCESS_TOKEN_EXPIRE_MINUTES * 60 + 5  # 5 s grace


# ── verify_token ──────────────────────────────────────────────────────────────

def _credentials_exception():
    return HTTPException(status_code=401, detail="Could not validate credentials")


def test_verify_token_returns_token_data():
    token = create_access_token({"sub": "user@test.com", "is_admin": False})
    token_data = verify_token(token, _credentials_exception())
    assert isinstance(token_data, TokenData)
    assert token_data.email == "user@test.com"


def test_verify_token_invalid_token_raises():
    with pytest.raises(HTTPException) as exc_info:
        verify_token("this.is.not.a.valid.jwt", _credentials_exception())
    assert exc_info.value.status_code == 401


def test_verify_token_tampered_signature_raises():
    token = create_access_token({"sub": "user@test.com", "is_admin": False})
    # Flip the last character to invalidate the signature
    tampered = token[:-1] + ("X" if token[-1] != "X" else "Y")
    with pytest.raises(HTTPException) as exc_info:
        verify_token(tampered, _credentials_exception())
    assert exc_info.value.status_code == 401


def test_verify_token_missing_sub_raises():
    """A token without 'sub' should trigger the credentials exception."""
    # Encode a token with no 'sub' claim
    raw = jwt.encode({"is_admin": False}, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        verify_token(raw, _credentials_exception())
    assert exc_info.value.status_code == 401

