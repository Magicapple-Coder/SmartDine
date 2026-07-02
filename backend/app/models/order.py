from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, func
from sqlalchemy.orm import relationship

from app.core.deps import Base


class Order(Base):
    """订单表，对应 sql/02_order.sql 的 order（V2: +merchant_id +discount_amount +actual_amount +is_group_order +member_count）"""

    __tablename__ = "order"

    order_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    member_id = Column(BigInteger, nullable=True)
    table_id = Column(BigInteger, nullable=True)
    source = Column(String(16), nullable=False)  # 堂食/外卖
    amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    actual_amount = Column(Numeric(10, 2), default=0)
    is_group_order = Column(SmallInteger, nullable=False, default=0)  # V2.0: 是否群体点餐
    member_count = Column(Integer, nullable=False, default=1)  # V2.0: 就餐人数
    pay_status = Column(SmallInteger, nullable=False, default=0)  # 0待付 1已付 2退款
    cook_status = Column(SmallInteger, nullable=False, default=0)  # 0待餐 1出餐 2完成
    created_at = Column(DateTime, server_default=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """订单明细表，对应 sql/02_order.sql 的 order_item（V2: +merchant_id）"""

    __tablename__ = "order_item"

    item_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    order_id = Column(BigInteger, ForeignKey("order.order_id"), nullable=False)
    dish_id = Column(BigInteger, ForeignKey("dish.dish_id"), nullable=False)
    qty = Column(Integer, nullable=False)
    note = Column(String(128))
    subtotal = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")


class Review(Base):
    """订单评价表，对应 sql/03_other.sql 的 review（V2: +merchant_id）"""

    __tablename__ = "review"

    review_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    order_id = Column(BigInteger, ForeignKey("order.order_id"), nullable=False)
    score = Column(SmallInteger, nullable=False)
    content = Column(String(500))
    sentiment = Column(String(8))  # 好评/中评/差评
    cause = Column(String(64))  # 差评归因
    created_at = Column(DateTime, server_default=func.now())
