from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_role
from app.db import get_db
from app.exceptions import AppError
from app.models.enums import UserRole
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

ManagerOrAdmin = Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager))]


@router.get(
    "/",
    response_model=list[ProductResponse],
    summary="List products",
)
async def list_products(
    _: Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager, UserRole.viewer))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Product]:
    result = await db.execute(select(Product).order_by(Product.id))
    return list(result.scalars().all())


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
)
async def create_product(
    body: ProductCreate,
    _: ManagerOrAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Product:
    supplier = await db.get(Supplier, body.supplier_id)
    if not supplier:
        raise AppError(404, f"Supplier {body.supplier_id} not found")
    existing = await db.execute(select(Product).where(Product.sku == body.sku))
    if existing.scalar_one_or_none():
        raise AppError(400, f"SKU {body.sku} already exists")
    product = Product(**body.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
)
async def get_product(
    product_id: int,
    _: Annotated[User, Depends(require_role(UserRole.admin, UserRole.manager, UserRole.viewer))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Product:
    product = await db.get(Product, product_id)
    if not product:
        raise AppError(404, f"Product {product_id} not found")
    return product


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
)
async def update_product(
    product_id: int,
    body: ProductUpdate,
    _: ManagerOrAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Product:
    product = await db.get(Product, product_id)
    if not product:
        raise AppError(404, f"Product {product_id} not found")
    data = body.model_dump(exclude_unset=True)
    if "supplier_id" in data:
        supplier = await db.get(Supplier, data["supplier_id"])
        if not supplier:
            raise AppError(404, f"Supplier {data['supplier_id']} not found")
    if "sku" in data:
        existing = await db.execute(
            select(Product).where(Product.sku == data["sku"], Product.id != product_id)
        )
        if existing.scalar_one_or_none():
            raise AppError(400, f"SKU {data['sku']} already exists")
    for key, value in data.items():
        setattr(product, key, value)
    await db.flush()
    await db.refresh(product)
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
)
async def delete_product(
    product_id: int,
    _: ManagerOrAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    product = await db.get(Product, product_id)
    if not product:
        raise AppError(404, f"Product {product_id} not found")
    await db.delete(product)
