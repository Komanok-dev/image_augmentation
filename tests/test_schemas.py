import pytest
from pydantic import ValidationError

from app.schemas import UserLogin, UserRegister

# ========================== Test user_login ========================


def test_user_login_valid():
    data = {"email": "valid@example.com", "password": "securepassword"}
    user_login = UserLogin(**data)
    assert user_login.email == "valid@example.com"
    assert user_login.password == "securepassword"


def test_user_login_invalid_email():
    data = {"email": "invalid-email", "password": "securepassword"}
    with pytest.raises(ValidationError) as exc_info:
        UserLogin(**data)
    assert "value is not a valid email address" in str(exc_info.value)


def test_user_login_missing_password():
    data = {"email": "valid@example.com"}
    with pytest.raises(ValidationError) as exc_info:
        UserLogin(**data)
    assert "Field required" in str(exc_info.value)
    assert "password" in str(exc_info.value)
    assert "type=missing" in str(exc_info.value)


# ========================= Test user_register =======================


def test_user_register_valid():
    data = {
        "email": "valid@example.com",
        "password": "securepassword",
        "first_name": "John",
        "last_name": "Doe",
    }
    user_register = UserRegister(**data)
    assert user_register.email == "valid@example.com"
    assert user_register.password == "securepassword"
    assert user_register.first_name == "John"
    assert user_register.last_name == "Doe"


def test_user_register_missing_first_name():
    data = {
        "email": "valid@example.com",
        "password": "securepassword",
        "last_name": "Doe",
    }
    with pytest.raises(ValidationError) as exc_info:
        UserRegister(**data)
    assert "Field required" in str(exc_info.value)
    assert "first_name" in str(exc_info.value)
    assert "type=missing" in str(exc_info.value)


def test_user_register_missing_last_name():
    data = {
        "email": "valid@example.com",
        "password": "securepassword",
        "first_name": "John",
    }
    with pytest.raises(ValidationError) as exc_info:
        UserRegister(**data)
    assert "Field required" in str(exc_info.value)
    assert "last_name" in str(exc_info.value)
    assert "type=missing" in str(exc_info.value)
