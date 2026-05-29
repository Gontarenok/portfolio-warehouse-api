import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/auth/register",
        json={"email": "newuser@test.com", "password": "password123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "viewer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@test.com", "password": "password123"}
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "login@test.com", "password": "password123"},
    )
    resp = await client.post(
        "/auth/login",
        json={"email": "login@test.com", "password": "password123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    resp = await client.post(
        "/auth/login",
        json={"email": "nobody@test.com", "password": "wrongpass1"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_success(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "me@test.com", "password": "password123"},
    )
    login = await client.post(
        "/auth/login",
        json={"email": "me@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@test.com"


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 403
