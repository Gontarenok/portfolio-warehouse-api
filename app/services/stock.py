from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.enums import MovementType
from app.models.movement import Movement
from app.models.product import Product
from app.models.stock_level import StockLevel
from app.models.warehouse import Warehouse
from app.schemas.movement import MovementCreate


async def _get_or_create_stock(
    db: AsyncSession, warehouse_id: int, product_id: int
) -> StockLevel:
    result = await db.execute(
        select(StockLevel).where(
            StockLevel.warehouse_id == warehouse_id,
            StockLevel.product_id == product_id,
        )
    )
    stock = result.scalar_one_or_none()
    if stock:
        return stock
    stock = StockLevel(warehouse_id=warehouse_id, product_id=product_id, quantity=0)
    db.add(stock)
    await db.flush()
    return stock


async def _adjust_stock(
    db: AsyncSession, warehouse_id: int, product_id: int, delta: int
) -> StockLevel:
    stock = await _get_or_create_stock(db, warehouse_id, product_id)
    new_qty = stock.quantity + delta
    if new_qty < 0:
        raise AppError(400, f"Insufficient stock at warehouse {warehouse_id} for product {product_id}")
    stock.quantity = new_qty
    stock.updated_at = datetime.now(timezone.utc)
    return stock


async def ensure_entities_exist(db: AsyncSession, data: MovementCreate) -> None:
    product = await db.get(Product, data.product_id)
    if not product:
        raise AppError(404, f"Product {data.product_id} not found")
    warehouse = await db.get(Warehouse, data.warehouse_id)
    if not warehouse:
        raise AppError(404, f"Warehouse {data.warehouse_id} not found")
    if data.type == "transfer":
        dest = await db.get(Warehouse, data.to_warehouse_id)
        if not dest:
            raise AppError(404, f"Destination warehouse {data.to_warehouse_id} not found")


def _movement_type(value: str) -> MovementType:
    mapping = {"in": MovementType.in_, "out": MovementType.out, "transfer": MovementType.transfer}
    return mapping[value]


async def create_movement(
    db: AsyncSession, data: MovementCreate, user_id: int
) -> Movement:
    await ensure_entities_exist(db, data)
    mtype = _movement_type(data.type)

    if mtype == MovementType.in_:
        await _adjust_stock(db, data.warehouse_id, data.product_id, data.quantity)
    elif mtype == MovementType.out:
        await _adjust_stock(db, data.warehouse_id, data.product_id, -data.quantity)
    else:
        await _adjust_stock(db, data.warehouse_id, data.product_id, -data.quantity)
        await _adjust_stock(db, data.to_warehouse_id, data.product_id, data.quantity)

    movement = Movement(
        warehouse_id=data.warehouse_id,
        product_id=data.product_id,
        type=mtype,
        quantity=data.quantity,
        reference=data.reference,
        to_warehouse_id=data.to_warehouse_id,
        created_by=user_id,
    )
    db.add(movement)
    await db.flush()
    await db.refresh(movement)
    return movement
