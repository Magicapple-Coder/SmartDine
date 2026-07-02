from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.repositories import dish as dish_repo
from app.repositories import order as order_repo
from app.schemas.order import OrderCreate, ReviewIn

SENTIMENT_THRESHOLDS = ((4, "好评"), (3, "中评"))


def create_order(db: Session, body: OrderCreate) -> Order:
    """下单：校验在售状态并计算金额，写入订单与明细。
    库存扣减（按 BOM）待库存模块完成后在此接入，见需求文档 3.6 智能体联动。
    """
    items_payload = []
    amount = Decimal("0")
    for item in body.items:
        dish = dish_repo.get_dish(db, item.dish_id)
        if dish is None or dish.status != 1:
            raise HTTPException(status_code=400, detail=f"菜品 {item.dish_id} 不可售")
        subtotal = Decimal(str(dish.price)) * item.qty
        amount += subtotal
        items_payload.append(
            {"dish_id": item.dish_id, "qty": item.qty, "note": item.note, "subtotal": subtotal}
        )
    return order_repo.create(db, body.table_id, amount, items_payload)


def get_order(db: Session, order_id: int) -> Order:
    order = order_repo.get(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


def list_orders(db: Session, pay_status: int | None = None, cook_status: int | None = None):
    """订单列表，供管理端订单管理页按支付/出餐状态筛选（需求文档 3.3）"""
    return order_repo.list_orders(db, pay_status, cook_status)


def update_status(db: Session, order_id: int, pay_status: int | None = None, cook_status: int | None = None) -> Order:
    order = get_order(db, order_id)
    return order_repo.update_status(db, order, pay_status, cook_status)


def _sentiment_for_score(score: int) -> str:
    for threshold, label in SENTIMENT_THRESHOLDS:
        if score >= threshold:
            return label
    return "差评"


def submit_review(db: Session, order_id: int, body: ReviewIn):
    """订单评价；差评（1-2 分）默认归因为「未填写」，供经营分析智能体后续归因分析（需求文档 3.3、5.4）"""
    get_order(db, order_id)  # 校验订单存在
    if not 1 <= body.score <= 5:
        raise HTTPException(status_code=400, detail="评分需在 1-5 之间")
    sentiment = _sentiment_for_score(body.score)
    cause = "未填写" if sentiment == "差评" else None
    return order_repo.create_review(db, order_id=order_id, score=body.score, content=body.content, sentiment=sentiment, cause=cause)


def delete_order(db: Session, order_id: int):
    """删除订单及其明细（同时清理关联评价记录）"""
    order = get_order(db, order_id)
    order_repo.delete_order(db, order)


def list_reviews(db: Session):
    """评价列表，供经营分析智能体/管理端统计好评率与差评归因（需求文档 5.4）"""
    return order_repo.list_reviews(db)
