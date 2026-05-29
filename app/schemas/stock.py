from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockLevelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    warehouse_id: int
    product_id: int
    quantity: int
    updated_at: datetime
