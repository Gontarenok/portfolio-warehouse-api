from fastapi import APIRouter

from app.api import auth, movements, products, stock, suppliers, warehouses

api_router = APIRouter(prefix="/api")
api_router.include_router(suppliers.router)
api_router.include_router(warehouses.router)
api_router.include_router(products.router)
api_router.include_router(stock.router)
api_router.include_router(movements.router)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_router.include_router(auth.router)
