import pytest
from httpx import AsyncClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.roomModels import Room
from backend.app.models.userModels import User
from backend.app.services.authService import hash_password

@pytest.fixture
def test_db():
    """Fixture to create a test database session."""
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
async def client():
    """Fixture to provide a FastAPI test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def test_user(test_db):
    """Fixture to create a test user."""
    user = User(username="testuser", email="test@example.com", password_hash=hash_password("testpassword"))
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
async def test_auth_token(client, test_user):
    """Fixture to authenticate test user and retrieve a token."""
    response = await client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    return response.json()["access_token"]

@pytest.fixture
def test_room(test_db, test_user):
    """Fixture to create a test room."""
    room = Room(name="Test Room", owner_id=test_user.id)
    test_db.add(room)
    test_db.commit()
    test_db.refresh(room)
    return room

async def test_create_room(client, test_auth_token):
    """Test room creation."""
    response = await client.post("/rooms/", json={"name": "New Room"}, headers={"Authorization": f"Bearer {test_auth_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Room"

async def test_create_room_duplicate(client, test_auth_token, test_room):
    """Test room creation with duplicate name."""
    response = await client.post("/rooms/", json={"name": "Test Room"}, headers={"Authorization": f"Bearer {test_auth_token}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Nome da sala já está em uso"

async def test_get_all_rooms(client):
    """Test retrieving all rooms."""
    response = await client.get("/rooms/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_room_by_id(client, test_room):
    """Test retrieving a room by ID."""
    response = await client.get(f"/rooms/{test_room.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Room"

async def test_update_room(client, test_auth_token, test_room):
    """Test updating a room name."""
    response = await client.put(f"/rooms/{test_room.id}", json={"name": "Updated Room"}, headers={"Authorization": f"Bearer {test_auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Room"

async def test_update_room_unauthorized(client, test_room):
    """Test unauthorized room update."""
    response = await client.put(f"/rooms/{test_room.id}", json={"name": "Illegal Update"})
    assert response.status_code == 401

async def test_delete_room(client, test_auth_token, test_room):
    """Test deleting a room."""
    response = await client.delete(f"/rooms/{test_room.id}", headers={"Authorization": f"Bearer {test_auth_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Sala deletada com sucesso."

async def test_delete_room_unauthorized(client, test_room):
    """Test unauthorized room deletion."""
    response = await client.delete(f"/rooms/{test_room.id}")
    assert response.status_code == 401
