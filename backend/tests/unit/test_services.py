import pytest
from unittest.mock import MagicMock

# Imports for user service tests
from app.services import user as user_service
from app.api.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash

# Imports for knowledge service tests
from app.services import knowledge as knowledge_service
from app.models.knowledge import KnowledgePoint


# --- Tests for user service ---

def test_create_user():
    """
    Test creating a new user.
    """
    # 1. Arrange
    mock_db = MagicMock()
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword"
    )

    # 2. Act
    created_user = user_service.create_user(db=mock_db, user_in=user_in)

    # 3. Assert
    assert created_user.username == user_in.username
    assert created_user.email == user_in.email
    assert created_user.password != user_in.password
    assert verify_password(user_in.password, created_user.password)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_get_user_by_email():
    """
    Test getting a user by email.
    """
    # Arrange
    mock_db = MagicMock()
    email = "test@example.com"
    mock_user = MagicMock()
    mock_user.email = email

    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Act
    user = user_service.get_user_by_email(db=mock_db, email=email)

    # Assert
    assert user is not None
    assert user.email == email
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_user_by_email_not_found():
    """
    Test getting a user by email when the user does not exist.
    """
    # Arrange
    mock_db = MagicMock()
    email = "nonexistent@example.com"

    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    user = user_service.get_user_by_email(db=mock_db, email=email)

    # Assert
    assert user is None
    mock_db.query.return_value.filter.return_value.first.assert_called_once()

def test_authenticate_user_success():
    """
    Test successful user authentication.
    """
    # Arrange
    mock_db = MagicMock()
    username = "testuser"
    password = "testpassword"

    mock_user = MagicMock()
    mock_user.username = username
    mock_user.password = get_password_hash(password)

    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Act
    authenticated_user = user_service.authenticate_user(db=mock_db, username=username, password=password)

    # Assert
    assert authenticated_user is not None
    assert authenticated_user.username == username

def test_authenticate_user_wrong_password():
    """
    Test user authentication with a wrong password.
    """
    # Arrange
    mock_db = MagicMock()
    username = "testuser"
    correct_password = "correctpassword"
    wrong_password = "wrongpassword"

    mock_user = MagicMock()
    mock_user.username = username
    mock_user.password = get_password_hash(correct_password)

    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Act
    authenticated_user = user_service.authenticate_user(db=mock_db, username=username, password=wrong_password)

    # Assert
    assert authenticated_user is None

def test_authenticate_user_not_found():
    """
    Test user authentication for a user that does not exist.
    """
    # Arrange
    mock_db = MagicMock()
    username = "nonexistentuser"
    password = "password"

    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    authenticated_user = user_service.authenticate_user(db=mock_db, username=username, password=password)

    # Assert
    assert authenticated_user is None


# --- Tests for knowledge service ---

def test_create_knowledge_point():
    """
    Test creating a new knowledge point.
    """
    # Arrange
    mock_db = MagicMock()
    kp_data = {
        "subject": "Math",
        "chapter": "Algebra",
        "section": "Equations",
        "item": "Linear Equations",
        "details": "Solving for x."
    }

    # Act
    created_kp = knowledge_service.create_knowledge_point(db=mock_db, knowledge_point_data=kp_data)

    # Assert
    assert created_kp.subject == kp_data["subject"]
    assert created_kp.chapter == kp_data["chapter"]
    assert created_kp.item == kp_data["item"]
    assert created_kp.mark_count == 0
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_get_knowledge_point_by_id():
    """
    Test getting a knowledge point by its ID.
    """
    # Arrange
    mock_db = MagicMock()
    kp_id = 1
    mock_kp = KnowledgePoint(id=kp_id, subject="Math", item="Test")

    mock_db.query.return_value.filter.return_value.first.return_value = mock_kp

    # Act
    kp = knowledge_service.get_knowledge_point_by_id(db=mock_db, knowledge_point_id=kp_id)

    # Assert
    assert kp is not None
    assert kp.id == kp_id
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_increment_knowledge_point_mark_count():
    """
    Test incrementing the mark count of a knowledge point.
    """
    # Arrange
    mock_db = MagicMock()
    kp_id = 1
    # We need a real object here to modify its attribute
    mock_kp = KnowledgePoint(id=kp_id, subject="Math", item="Test", mark_count=5)

    # The get_knowledge_point_by_id call inside the service function will use this mock
    mock_db.query.return_value.filter.return_value.first.return_value = mock_kp

    # Act
    updated_kp = knowledge_service.increment_knowledge_point_mark_count(db=mock_db, knowledge_point_id=kp_id)

    # Assert
    assert updated_kp is not None
    assert updated_kp.mark_count == 6
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_kp)
