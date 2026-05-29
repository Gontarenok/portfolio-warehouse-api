from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import MovementType


class MovementCreate(BaseModel):
    warehouse_id: int = Field(examples=[1], description="Source warehouse for out/transfer; target for in")
    product_id: int = Field(examples=[1])
    type: Literal["in", "out", "transfer"] = Field(examples=["in"])
    quantity: int = Field(gt=0, examples=[10])
    reference: str | None = Field(default=None, examples=["PO-2024-001"])
    to_warehouse_id: int | None = Field(
        default=None,
        examples=[2],
        description="Required for transfer: destination warehouse",
    )

    @model_validator(mode="after")
    def validate_transfer(self) -> "MovementCreate":
        if self.type == "transfer" and self.to_warehouse_id is None:
            raise ValueError("to_warehouse_id is required for transfer movements")
        if self.type == "transfer" and self.to_warehouse_id == self.warehouse_id:
            raise ValueError("to_warehouse_id must differ from warehouse_id")
        return self


class MovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    warehouse_id: int
    product_id: int
    type: MovementType
    quantity: int
    reference: str | None
    to_warehouse_id: int | None
    created_by: int
    created_at: datetime
