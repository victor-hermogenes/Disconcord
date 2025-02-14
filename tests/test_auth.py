import pytest
from httpx import AsyncClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
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

async def test_register(client):
    """Test user registration."""
    response = await client.post("/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["username"] == "newuser"

async def test_register_existing_user(client, test_user):
    """Test registration with an existing username/email."""
    response = await client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "newpassword"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário ou e-mail já está em uso."

async def test_login(client, test_user):
    """Test successful login."""
    response = await client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "testuser"

async def test_login_invalid_credentials(client):
    """Test login with incorrect credentials."""
    response = await client.post("/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas."

async def test_get_current_user(client, test_user):
    """Test retrieving the current user with a valid token."""
    login_response = await client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]

    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

async def test_get_current_user_invalid_token(client):
    """Test retrieving current user with an invalid token."""
    response = await client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expirado ou inválido."

async def test_logout(client):
    """Test user logout (deletes cookie)."""
    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Deslogou com sucesso."
