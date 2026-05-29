from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255, examples=["Acme Supplies"])
    contact_email: EmailStr | None = Field(default=None, examples=["sales@acme.com"])
    contact_phone: str | None = Field(default=None, examples=["+1-555-0100"])
    address: str | None = Field(default=None, examples=["123 Industrial Blvd"])


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    address: str | None = None


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_email: str | None
    contact_phone: str | None
    address: str | None
    created_at: datetime
