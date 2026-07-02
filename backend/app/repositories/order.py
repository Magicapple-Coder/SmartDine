from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.models.order import Order, OrderItem, Review


def _mid() -> int:
    return current_merchant_id.get() or 1


def create(db: Session, table_id: int | None, amount: Decimal, items: list[dict]) -> Order:
    mid = _mid()
    order = Order(
        merchant_id=mid,
        table_id=table_id,
        source="堂食" if table_id else "外卖",
        amount=amount,
        pay_status=0,
        cook_status=0,
    )
    for item in items:
        item["merchant_id"] = mid
    order.items = [OrderItem(**item) for item in items]
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get(db: Session, order_id: int) -> Order | None:
    mid = _mid()
    return db.query(Order).filter(Order.order_id == order_id, Order.merchant_id == mid).first()


def list_orders(db: Session, pay_status: int | None = None, cook_status: int | None = None):
    mid = _mid()
    query = db.query(Order).filter(Order.merchant_id == mid)
    if pay_status is not None:
        query = query.filter(Order.pay_status == pay_status)
    if cook_status is not None:
        query = query.filter(Order.cook_status == cook_status)
    return query.order_by(Order.created_at.desc()).all()


def update_status(db: Session, order: Order, pay_status: int | None = None, cook_status: int | None = None) -> Order:
    if pay_status is not None:
        order.pay_status = pay_status
    if cook_status is not None:
        order.cook_status = cook_status
    db.commit()
    db.refresh(order)
    return order


def create_review(db: Session, **kwargs) -> Review:
    kwargs.setdefault("merchant_id", _mid())
    review = Review(**kwargs)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_order(db: Session, order: Order) -> None:
    """删除订单及其关联明细（Review 外键约束：先删关联评价）"""
    mid = _mid()
    # 先删除关联的评价
    db.query(Review).filter(Review.order_id == order.order_id, Review.merchant_id == mid).delete()
    db.delete(order)
    db.commit()


def list_reviews(db: Session):
    mid = _mid()
    return db.query(Review).filter(Review.merchant_id == mid).order_by(Review.created_at.desc()).all()
