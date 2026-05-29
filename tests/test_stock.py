import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_stock_success(client: AsyncClient, manager_token: str, auth_header):
    resp = await client.get("/api/stock/", headers=auth_header(manager_token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_stock_unauthorized(client: AsyncClient):
    resp = await client.get("/api/stock/")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_stock_filtered(
    client: AsyncClient, admin_token: str, manager_token: str, auth_header
):
    wh = await client.post(
        "/api/warehouses/",
        headers=auth_header(admin_token),
        json={"name": "Stock WH"},
    )
    wid = wh.json()["id"]
    sup = await client.post(
        "/api/suppliers/",
        headers=auth_header(manager_token),
        json={"name": "Stock Sup"},
    )
    prod = await client.post(
        "/api/products/",
        headers=auth_header(manager_token),
        json={"sku": "STK-1", "name": "P", "supplier_id": sup.json()["id"], "unit_price": "1"},
    )
    await client.post(
        "/api/movements/",
        headers=auth_header(manager_token),
        json={
            "warehouse_id": wid,
            "product_id": prod.json()["id"],
            "type": "in",
            "quantity": 5,
        },
    )
    resp = await client.get(
        f"/api/stock/?warehouse_id={wid}&product_id={prod.json()['id']}",
        headers=auth_header(manager_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["quantity"] == 5
