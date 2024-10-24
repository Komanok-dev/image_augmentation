from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException, status

from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    user_authorization,
    verify_password,
)
from app.models import User
from app.schemas import UserLogin
from app.settings import auth_settings

# ======================= Test get_password_hash =====================


def test_get_password_hash():
    password = "securepassword"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0


# ======================= Test verify_password =======================


def test_verify_password_success():
    password = "securepassword"
    hashed_password = get_password_hash(password)
    result = verify_password(password, hashed_password)
    assert result is True


def test_verify_password_failure():
    correct_password = "securepassword"
    wrong_password = "wrongpassword"
    hashed_password = get_password_hash(correct_password)
    result = verify_password(wrong_password, hashed_password)
    assert result is False


def test_verify_password_empty_string():
    password = "securepassword"
    hashed_password = get_password_hash(password)
    result = verify_password("", hashed_password)
    assert result is False


# ====================== Test authenticate_user ======================


def mock_verify_password(input_password, stored_password):
    return input_password == stored_password


def test_authenticate_user_success(mock_db_session, monkeypatch):
    email = "test@example.com"
    password = "securepassword"
    user = User(email=email, password=password)
    mock_db_session.query().filter().first.return_value = user
    monkeypatch.setattr("app.auth.verify_password", mock_verify_password)
    result = authenticate_user(email, password, mock_db_session)
    assert result == user


def test_authenticate_user_invalid_email(mock_db_session):
    email = "nonexistent@example.com"
    password = "securepassword"
    mock_db_session.query().filter().first.return_value = None
    result = authenticate_user(email, password, mock_db_session)
    assert result is False


def test_authenticate_user_invalid_password(mock_db_session, monkeypatch):
    email = "test@example.com"
    password = "wrongpassword"
    stored_password = "securepassword"
    user = User(email=email, password=stored_password)
    mock_db_session.query().filter().first.return_value = user
    monkeypatch.setattr("app.auth.verify_password", mock_verify_password)
    result = authenticate_user(email, password, mock_db_session)
    assert result is False


# ===================== Test create_access_token =====================


def test_create_access_token():
    data = {"sub": "user_id"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_expiration():
    data = {"sub": "user_id"}
    expires_delta = timedelta(minutes=5)
    expected_expiry = datetime.now(timezone.utc) + expires_delta
    token = create_access_token(data, expires_delta)
    decoded_token = jwt.decode(
        token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM]
    )
    assert "exp" in decoded_token
    token_expiry = datetime.fromtimestamp(
        decoded_token["exp"], tz=timezone.utc
    )
    assert abs((token_expiry - expected_expiry).total_seconds()) < 10


def test_create_access_token_data():
    data = {"sub": "user_id", "role": "admin"}
    expires_delta = timedelta(minutes=10)
    token = create_access_token(data, expires_delta)
    decoded_token = jwt.decode(
        token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM]
    )
    assert decoded_token["sub"] == "user_id"
    assert decoded_token["role"] == "admin"
    assert "exp" in decoded_token


# ===================== Test user_authorization ======================


@pytest.mark.asyncio
async def test_user_authorization_success(mock_async_db_session, monkeypatch):
    form_data = UserLogin(email="test@example.com", password="correctpassword")
    user = User(email=form_data.email, password="hashedpassword")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_async_db_session.execute.return_value = mock_result
    monkeypatch.setattr(
        "app.auth.pwd_context.verify", lambda p, h: p == "correctpassword"
    )
    monkeypatch.setattr(
        "app.auth.create_access_token",
        lambda data, expires_delta: "mocked_token",
    )
    token = await user_authorization(form_data, mock_async_db_session)
    assert token == "mocked_token"


@pytest.mark.asyncio
async def test_user_authorization_invalid_email(mock_async_db_session):
    form_data = UserLogin(email="invalid@example.com", password="password")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_async_db_session.execute.return_value = mock_result
    with pytest.raises(HTTPException) as exc_info:
        await user_authorization(form_data, mock_async_db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Incorrect email or password"


@pytest.mark.asyncio
async def test_user_authorization_invalid_password(
    mock_async_db_session, monkeypatch
):
    form_data = UserLogin(email="test@example.com", password="wrongpassword")
    user = User(email=form_data.email, password="hashedpassword")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_async_db_session.execute.return_value = mock_result
    monkeypatch.setattr("app.auth.pwd_context.verify", lambda p, h: False)
    with pytest.raises(HTTPException) as exc_info:
        await user_authorization(form_data, mock_async_db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Incorrect email or password"


# ====================== Test get_current_user =======================


@pytest.mark.asyncio
async def test_get_current_user_valid_token(mock_async_db_session):
    token_data = {"sub": "test@example.com"}
    token = jwt.encode(
        token_data, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM
    )
    user = User(email="test@example.com", password="hashedpassword")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_async_db_session.execute.return_value = mock_result
    result = await get_current_user(token, mock_async_db_session)
    assert result == user


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_async_db_session):
    invalid_token = "invalid.token"
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(invalid_token, mock_async_db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_missing_sub(mock_async_db_session):
    token_data = {}
    token = jwt.encode(
        token_data, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, mock_async_db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(mock_async_db_session):
    token_data = {"sub": "nonexistent@example.com"}
    token = jwt.encode(
        token_data, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_async_db_session.execute.return_value = mock_result
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, mock_async_db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"
