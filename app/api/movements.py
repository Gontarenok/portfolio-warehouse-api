from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.db import get_db
from app.models.enums import MovementType, UserRole
from app.models.movement import Movement
from app.models.user import User
from app.schemas.movement import MovementCreate, MovementResponse
from app.services.stock import create_movement

router = APIRouter(prefix="/movements", tags=["Movements"])

ManagerOrAdmin = Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager))]


@router.post(
    "/",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record stock movement",
    description="Creates movement and updates StockLevel automatically (in/out/transfer).",
)
async def post_movement(
    body: MovementCreate,
    user: ManagerOrAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Movement:
    return await create_movement(db, body, user.id)


@router.get(
    "/",
    response_model=list[MovementResponse],
    summary="List movements",
    description="Filter by date range (from/to ISO datetime) and movement type.",
)
async def list_movements(
    _: Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager, UserRole.viewer))],
    db: Annotated[AsyncSession, Depends(get_db)],
    from_: datetime | None = Query(default=None, alias="from", examples=["2024-01-01T00:00:00Z"]),
    to: datetime | None = Query(default=None, examples=["2024-12-31T23:59:59Z"]),
    type: MovementType | None = Query(default=None, examples=["in"]),
) -> list[Movement]:
    stmt = select(Movement).order_by(Movement.created_at.desc())
    if from_ is not None:
        stmt = stmt.where(Movement.created_at >= from_)
    if to is not None:
        stmt = stmt.where(Movement.created_at <= to)
    if type is not None:
        stmt = stmt.where(Movement.type == type)
    result = await db.execute(stmt)
    return list(result.scalars().all())
