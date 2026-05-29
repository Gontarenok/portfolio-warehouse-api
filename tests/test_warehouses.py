import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_warehouses_success(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.get("/api/warehouses/", headers=auth_header(manager_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_warehouses_unauthorized(client: AsyncClient):
    resp = await client.get("/api/warehouses/")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_warehouse_success(client: AsyncClient, admin_token: str, auth_header):
    resp = await client.post(
        "/api/warehouses/",
        headers=auth_header(admin_token),
        json={"name": "Main", "address": "Addr 1"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Main"


@pytest.mark.asyncio
async def test_create_warehouse_forbidden_manager(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.post(
        "/api/warehouses/",
        headers=auth_header(manager_token),
        json={"name": "Blocked"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_warehouse_success(client: AsyncClient, admin_token: str, auth_header):
    created = await client.post(
        "/api/warehouses/",
        headers=auth_header(admin_token),
        json={"name": "WH1"},
    )
    wid = created.json()["id"]
    resp = await client.get(f"/api/warehouses/{wid}", headers=auth_header(admin_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_warehouse_not_found(client: AsyncClient, admin_token: str, auth_header):
    resp = await client.get("/api/warehouses/9999", headers=auth_header(admin_token))
    assert resp.status_code == 404
