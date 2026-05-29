from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64, examples=["SKU-001"])
    name: str = Field(min_length=1, max_length=255, examples=["Widget A"])
    description: str | None = Field(default=None, examples=["Standard widget"])
    supplier_id: int = Field(examples=[1])
    unit_price: Decimal = Field(ge=0, examples=["19.99"])


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    supplier_id: int | None = None
    unit_price: Decimal | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str | None
    supplier_id: int
    unit_price: Decimal
    created_at: datetime
