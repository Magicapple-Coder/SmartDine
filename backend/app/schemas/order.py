from pydantic import BaseModel, ConfigDict


class OrderItemIn(BaseModel):
    dish_id: int
    qty: int
    note: str | None = None


class OrderCreate(BaseModel):
    """下单请求体，对应 POST /api/v1/orders"""

    table_id: int | None = None
    items: list[OrderItemIn]


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    dish_id: int
    qty: int
    note: str | None = None
    subtotal: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    table_id: int | None
    amount: float
    pay_status: int
    cook_status: int
    items: list[OrderItemOut]


class ReviewIn(BaseModel):
    score: int  # 1-5
    content: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: int
    order_id: int
    score: int
    content: str | None = None
    sentiment: str | None = None
    cause: str | None = None
