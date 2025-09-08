import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge import KnowledgePoint

# Helper function to get auth headers
def get_auth_headers(client: TestClient, username="test_kp_user", password="password") -> dict:
    """
    Register and log in a user, return auth headers.
    """
    # Use a unique email for each user to avoid conflicts between tests
    email = f"{username}@example.com"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": username, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_knowledge_point(client: TestClient, db_session: Session):
    """
    Test creating a new knowledge point successfully.
    """
    # Arrange
    headers = get_auth_headers(client, username="creator_user")
    kp_data = {
        "subject": "Physics",
        "chapter": "Mechanics",
        "section": "Newton's Laws",
        "item": "First Law",
        "details": "An object at rest stays at rest...",
    }

    # Act
    response = client.post(f"{settings.API_V1_STR}/knowledge/", json=kp_data, headers=headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["item"] == kp_data["item"]
    assert data["subject"] == kp_data["subject"]

    # Verify in DB
    kp_in_db = db_session.query(KnowledgePoint).filter(KnowledgePoint.id == data["id"]).first()
    assert kp_in_db is not None
    assert kp_in_db.item == kp_data["item"]


def test_create_knowledge_point_unauthenticated(client: TestClient):
    """
    Test that creating a knowledge point fails without authentication.
    """
    # Arrange
    kp_data = {"subject": "Test", "chapter": "Test", "section": "Test", "item": "Test"}

    # Act
    response = client.post(f"{settings.API_V1_STR}/knowledge/", json=kp_data)

    # Assert
    assert response.status_code == 401 # Unauthorized


def test_get_knowledge_point(client: TestClient, db_session: Session):
    """
    Test retrieving a single knowledge point by its ID.
    """
    # Arrange
    headers = get_auth_headers(client, username="getter_user")
    # Create a knowledge point first
    kp = KnowledgePoint(subject="History", chapter="Ancient", section="Rome", item="Colosseum")
    db_session.add(kp)
    db_session.commit()
    db_session.refresh(kp)

    # Act
    response = client.get(f"{settings.API_V1_STR}/knowledge/{kp.id}", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == kp.id
    assert data["item"] == "Colosseum"


def test_get_knowledge_point_not_found(client: TestClient):
    """
    Test that a 404 is returned for a non-existent knowledge point.
    """
    # Arrange
    headers = get_auth_headers(client, username="notfound_user")
    non_existent_id = 99999

    # Act
    response = client.get(f"{settings.API_V1_STR}/knowledge/{non_existent_id}", headers=headers)

    # Assert
    assert response.status_code == 404


def test_search_knowledge_points(client: TestClient, db_session: Session):
    """
    Test searching for knowledge points with query parameters.
    """
    # Arrange
    headers = get_auth_headers(client, username="searcher_user")
    # Create some data to search for
    kp1 = KnowledgePoint(subject="Chemistry", chapter="Organic", section="Alkanes", item="Methane")
    kp2 = KnowledgePoint(subject="Chemistry", chapter="Organic", section="Alkenes", item="Ethene")
    kp3 = KnowledgePoint(subject="Biology", chapter="Cells", section="Organelles", item="Mitochondria")
    db_session.add_all([kp1, kp2, kp3])
    db_session.commit()

    # Act: Search for all knowledge points in the "Chemistry" subject
    response = client.get(f"{settings.API_V1_STR}/knowledge/search?subject=Chemistry", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    items = {item["item"] for item in data}
    assert "Methane" in items
    assert "Ethene" in items
    assert "Mitochondria" not in items
