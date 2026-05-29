from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.db import get_db
from app.exceptions import AppError
from app.models.enums import UserRole
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.supplier import SupplierCreate, SupplierResponse, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

ManagerOrAdmin = Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager))]


@router.get(
    "/",
    response_model=list[SupplierResponse],
    summary="List all suppliers",
)
async def list_suppliers(
    _: Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager, UserRole.viewer))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Supplier]:
    result = await db.execute(select(Supplier).order_by(Supplier.id))
    return list(result.scalars().all())


@router.post(
    "/",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create supplier",
    description="Requires admin or manager role.",
)
async def create_supplier(
    body: SupplierCreate,
    _: ManagerOrAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Supplier:
    supplier = Supplier(**body.model_dump())
    db.add(supplier)
    await db.flush()
    await db.refresh(supplier)
    return supplier


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Get supplier by ID",
)
async def get_supplier(
    supplier_id: int,
    _: Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager, UserRole.viewer))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Supplier:
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise AppError(404, f"Supplier {supplier_id} not found")
    return supplier


@router.patch(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Update supplier",
)
async def update_supplier(
    supplier_id: int,
    body: SupplierUpdate,
    _: ManagerOrAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Supplier:
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise AppError(404, f"Supplier {supplier_id} not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(supplier, key, value)
    await db.flush()
    await db.refresh(supplier)
    return supplier


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete supplier",
)
async def delete_supplier(
    supplier_id: int,
    _: ManagerOrAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise AppError(404, f"Supplier {supplier_id} not found")
    await db.delete(supplier)
