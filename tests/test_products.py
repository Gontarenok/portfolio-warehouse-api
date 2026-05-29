import pytest
from httpx import AsyncClient


async def _supplier_id(client, token, auth_header) -> int:
    resp = await client.post(
        "/api/suppliers/",
        headers=auth_header(token),
        json={"name": "Prod Supplier"},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_products_success(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.get("/api/products/", headers=auth_header(manager_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_products_unauthorized(client: AsyncClient):
    resp = await client.get("/api/products/")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_product_success(client: AsyncClient, manager_token: str, auth_header):
    sid = await _supplier_id(client, manager_token, auth_header)
    resp = await client.post(
        "/api/products/",
        headers=auth_header(manager_token),
        json={
            "sku": "SKU-100",
            "name": "Widget",
            "supplier_id": sid,
            "unit_price": "9.99",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["sku"] == "SKU-100"


@pytest.mark.asyncio
async def test_create_product_supplier_not_found(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.post(
        "/api/products/",
        headers=auth_header(manager_token),
        json={
            "sku": "SKU-404",
            "name": "X",
            "supplier_id": 9999,
            "unit_price": "1.00",
        },
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_product_success(client: AsyncClient, manager_token: str, auth_header):
    sid = await _supplier_id(client, manager_token, auth_header)
    created = await client.post(
        "/api/products/",
        headers=auth_header(manager_token),
        json={"sku": "SKU-GET", "name": "G", "supplier_id": sid, "unit_price": "1"},
    )
    pid = created.json()["id"]
    resp = await client.get(f"/api/products/{pid}", headers=auth_header(manager_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.get("/api/products/9999", headers=auth_header(manager_token))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_product_success(client: AsyncClient, manager_token: str, auth_header):
    sid = await _supplier_id(client, manager_token, auth_header)
    created = await client.post(
        "/api/products/",
        headers=auth_header(manager_token),
        json={"sku": "SKU-UPD", "name": "Old", "supplier_id": sid, "unit_price": "1"},
    )
    pid = created.json()["id"]
    resp = await client.patch(
        f"/api/products/{pid}",
        headers=auth_header(manager_token),
        json={"name": "New"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"


@pytest.mark.asyncio
async def test_delete_product_success(client: AsyncClient, manager_token: str, auth_header):
    sid = await _supplier_id(client, manager_token, auth_header)
    created = await client.post(
        "/api/products/",
        headers=auth_header(manager_token),
        json={"sku": "SKU-DEL", "name": "D", "supplier_id": sid, "unit_price": "1"},
    )
    pid = created.json()["id"]
    resp = await client.delete(f"/api/products/{pid}", headers=auth_header(manager_token))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_product_not_found(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.delete("/api/products/9999", headers=auth_header(manager_token))
    assert resp.status_code == 404
