from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    stock_levels: Mapped[list["StockLevel"]] = relationship(back_populates="warehouse")
    movements: Mapped[list["Movement"]] = relationship(
        back_populates="warehouse",
        foreign_keys="Movement.warehouse_id",
    )
