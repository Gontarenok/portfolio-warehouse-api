import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_suppliers_success(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.get("/api/suppliers/", headers=auth_header(manager_token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_suppliers_unauthorized(client: AsyncClient):
    resp = await client.get("/api/suppliers/")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_supplier_success(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.post(
        "/api/suppliers/",
        headers=auth_header(manager_token),
        json={"name": "Test Supplier", "contact_email": "s@test.com"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Test Supplier"


@pytest.mark.asyncio
async def test_create_supplier_forbidden_viewer(client: AsyncClient):
    reg = await client.post(
        "/auth/register",
        json={"email": "viewer@test.com", "password": "password123"},
    )
    login = await client.post(
        "/auth/login",
        json={"email": "viewer@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    resp = await client.post(
        "/api/suppliers/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Blocked"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_supplier_success(client: AsyncClient, manager_token: str, auth_header):
    created = await client.post(
        "/api/suppliers/",
        headers=auth_header(manager_token),
        json={"name": "Get Me"},
    )
    sid = created.json()["id"]
    resp = await client.get(f"/api/suppliers/{sid}", headers=auth_header(manager_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_supplier_not_found(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.get("/api/suppliers/9999", headers=auth_header(manager_token))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_supplier_success(client: AsyncClient, manager_token: str, auth_header):
    created = await client.post(
        "/api/suppliers/",
        headers=auth_header(manager_token),
        json={"name": "Old Name"},
    )
    sid = created.json()["id"]
    resp = await client.patch(
        f"/api/suppliers/{sid}",
        headers=auth_header(manager_token),
        json={"name": "New Name"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_supplier_success(client: AsyncClient, manager_token: str, auth_header):
    created = await client.post(
        "/api/suppliers/",
        headers=auth_header(manager_token),
        json={"name": "To Delete"},
    )
    sid = created.json()["id"]
    resp = await client.delete(f"/api/suppliers/{sid}", headers=auth_header(manager_token))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_supplier_not_found(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.delete("/api/suppliers/9999", headers=auth_header(manager_token))
    assert resp.status_code == 404
