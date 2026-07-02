from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SupplierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: int
    name: str
    category: str | None = None
    contact: str | None = None
    phone: str | None = None
    status: int
    lead_time: int


class SupplierCreate(BaseModel):
    name: str
    category: str | None = None
    contact: str | None = None
    phone: str | None = None
    lead_time: int = 1


class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ingredient_id: int
    supplier_id: int | None = None
    name: str
    unit: str
    stock: Decimal
    safe_threshold: Decimal


class IngredientCreate(BaseModel):
    name: str
    unit: str
    supplier_id: int | None = None
    stock: Decimal = Decimal("0")
    safe_threshold: Decimal = Decimal("0")


class StockLogIn(BaseModel):
    ingredient_id: int
    type: str  # 入库/出库/损耗
    qty: Decimal
    operator: str
    remark: str | None = None


class StockLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: int
    ingredient_id: int
    type: str
    qty: Decimal
    operator: str
    time: datetime
    remark: str | None = None
