import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User

def test_register_user_success(client: TestClient, db_session: Session):
    """
    Test successful user registration.
    """
    # Arrange
    user_data = {
        "username": "testuser_integration",
        "email": "test_integration@example.com",
        "password": "testpassword"
    }

    # Act
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)

    # Assert
    assert response.status_code == 200 # The endpoint returns 200 OK, not 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data

    # Verify user in DB
    user_in_db = db_session.query(User).filter(User.username == user_data["username"]).first()
    assert user_in_db is not None
    assert user_in_db.email == user_data["email"]


def test_register_user_duplicate_username(client: TestClient):
    """
    Test registration with a duplicate username.
    """
    # Arrange: Create a user first
    user_data = {
        "username": "duplicate_user",
        "email": "unique1@example.com",
        "password": "password"
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)

    # Act: Try to register again with the same username
    duplicate_data = {
        "username": "duplicate_user",
        "email": "unique2@example.com",
        "password": "password"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=duplicate_data)

    # Assert
    assert response.status_code == 400
    assert "用户名已被注册" in response.json()["detail"]


def test_login_for_access_token_success(client: TestClient):
    """
    Test successful login and token generation.
    """
    # Arrange: Create a user first
    username = "login_user"
    password = "login_password"
    user_data = {
        "username": username,
        "email": "login@example.com",
        "password": password
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)

    # Act: Login with form data
    login_data = {"username": username, "password": password}
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)

    # Assert
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_for_access_token_wrong_password(client: TestClient):
    """
    Test login with an incorrect password.
    """
    # Arrange: Create a user
    username = "wrong_pass_user"
    password = "correct_password"
    user_data = {
        "username": username,
        "email": "wrongpass@example.com",
        "password": password
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)

    # Act: Attempt to login with the wrong password
    login_data = {"username": username, "password": "this_is_wrong"}
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)

    # Assert
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]


def test_login_for_access_token_user_not_found(client: TestClient):
    """
    Test login for a user that does not exist.
    """
    # Arrange
    login_data = {"username": "nonexistent_user", "password": "password"}

    # Act
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)

    # Assert
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]
