from sqlalchemy import BigInteger, Column, DateTime, Integer, JSON, Numeric, SmallInteger, String, func

from app.core.deps import Base


class Dish(Base):
    """菜品表，对应 sql/01_menu_inventory.sql 的 dish（V2: +merchant_id +cost_price +nutrition +recommended_weight +total_sales）"""

    __tablename__ = "dish"

    dish_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    name = Column(String(64), nullable=False)
    category = Column(String(16), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), default=0)
    tags = Column(String(128))
    allergens = Column(String(128))
    nutrition = Column(JSON, nullable=True)  # V2.0: {热量,蛋白质,碳水,脂肪}
    status = Column(SmallInteger, nullable=False, default=1)  # 1 在售 0 停售
    weekly_sales = Column(Integer, nullable=False, default=0)
    total_sales = Column(Integer, nullable=False, default=0)  # V2.0: 历史总销量
    recommended_weight = Column(Integer, nullable=False, default=5)  # V2.0: 推荐权重 1-10
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
