import pytest
from httpx import AsyncClient


async def _setup_product_warehouse(client, admin_token, manager_token, auth_header):
    wh = await client.post(
        "/api/warehouses/",
        headers=auth_header(admin_token),
        json={"name": "MV WH"},
    )
    sup = await client.post(
        "/api/suppliers/",
        headers=auth_header(manager_token),
        json={"name": "MV Sup"},
    )
    prod = await client.post(
        "/api/products/",
        headers=auth_header(manager_token),
        json={
            "sku": "MV-1",
            "name": "Move Product",
            "supplier_id": sup.json()["id"],
            "unit_price": "10",
        },
    )
    return wh.json()["id"], prod.json()["id"]


@pytest.mark.asyncio
async def test_create_movement_in_success(
    client: AsyncClient, admin_token: str, manager_token: str, auth_header
):
    wid, pid = await _setup_product_warehouse(client, admin_token, manager_token, auth_header)
    resp = await client.post(
        "/api/movements/",
        headers=auth_header(manager_token),
        json={"warehouse_id": wid, "product_id": pid, "type": "in", "quantity": 20},
    )
    assert resp.status_code == 201
    assert resp.json()["type"] == "in"


@pytest.mark.asyncio
async def test_create_movement_out_insufficient(
    client: AsyncClient, admin_token: str, manager_token: str, auth_header
):
    wid, pid = await _setup_product_warehouse(client, admin_token, manager_token, auth_header)
    resp = await client.post(
        "/api/movements/",
        headers=auth_header(manager_token),
        json={"warehouse_id": wid, "product_id": pid, "type": "out", "quantity": 1},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_movement_forbidden_viewer(client: AsyncClient, admin_token: str, auth_header):
    await client.post(
        "/auth/register",
        json={"email": "v2@test.com", "password": "password123"},
    )
    login = await client.post(
        "/auth/login",
        json={"email": "v2@test.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    resp = await client.post(
        "/api/movements/",
        headers={"Authorization": f"Bearer {token}"},
        json={"warehouse_id": 1, "product_id": 1, "type": "in", "quantity": 1},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_movements_success(
    client: AsyncClient, admin_token: str, manager_token: str, auth_header
):
    wid, pid = await _setup_product_warehouse(client, admin_token, manager_token, auth_header)
    await client.post(
        "/api/movements/",
        headers=auth_header(manager_token),
        json={"warehouse_id": wid, "product_id": pid, "type": "in", "quantity": 3},
    )
    resp = await client.get("/api/movements/", headers=auth_header(manager_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_list_movements_unauthorized(client: AsyncClient):
    resp = await client.get("/api/movements/")
    assert resp.status_code == 403
