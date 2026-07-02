from pydantic import BaseModel, ConfigDict


class DishOut(BaseModel):
    """菜品查询响应（管理端/用户端/智能体上下文共用）"""

    model_config = ConfigDict(from_attributes=True)

    dish_id: int
    name: str
    category: str
    price: float
    tags: str | None = None
    allergens: str | None = None
    status: int
    weekly_sales: int


class DishCreate(BaseModel):
    name: str
    category: str
    price: float
    tags: str | None = None
    allergens: str | None = None


class DishUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: float | None = None
    tags: str | None = None
    allergens: str | None = None
