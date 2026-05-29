from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.db import get_db
from app.models.enums import UserRole
from app.models.stock_level import StockLevel
from app.models.user import User
from app.schemas.stock import StockLevelResponse

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get(
    "/",
    response_model=list[StockLevelResponse],
    summary="Query stock levels",
    description="Filter by warehouse_id and/or product_id. All authenticated roles.",
)
async def list_stock(
    _: Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager, UserRole.viewer))],
    db: Annotated[AsyncSession, Depends(get_db)],
    warehouse_id: int | None = Query(default=None, examples=[1]),
    product_id: int | None = Query(default=None, examples=[1]),
) -> list[StockLevel]:
    stmt = select(StockLevel).order_by(StockLevel.id)
    if warehouse_id is not None:
        stmt = stmt.where(StockLevel.warehouse_id == warehouse_id)
    if product_id is not None:
        stmt = stmt.where(StockLevel.product_id == product_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
