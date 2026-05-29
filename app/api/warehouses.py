from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.db import get_db
from app.exceptions import AppError
from app.models.enums import UserRole
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseResponse

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])

AdminOnly = Annotated[User, Depends(require_role(UserRole.admin))]


@router.get(
    "/",
    response_model=list[WarehouseResponse],
    summary="List warehouses",
    description="All authenticated users can list warehouses.",
)
async def list_warehouses(
    _: Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager, UserRole.viewer))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Warehouse]:
    result = await db.execute(select(Warehouse).order_by(Warehouse.id))
    return list(result.scalars().all())


@router.post(
    "/",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create warehouse",
    description="Admin only.",
)
async def create_warehouse(
    body: WarehouseCreate,
    _: AdminOnly,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Warehouse:
    warehouse = Warehouse(**body.model_dump())
    db.add(warehouse)
    await db.flush()
    await db.refresh(warehouse)
    return warehouse


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
    summary="Get warehouse by ID",
)
async def get_warehouse(
    warehouse_id: int,
    _: Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager, UserRole.viewer))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Warehouse:
    warehouse = await db.get(Warehouse, warehouse_id)
    if not warehouse:
        raise AppError(404, f"Warehouse {warehouse_id} not found")
    return warehouse
