from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.schemas.order import OrderCreate, OrderOut, ReviewIn, ReviewOut
from app.services import order as order_service

router = APIRouter(prefix="/orders", tags=["订单"])


@router.post("")
def create_order(body: OrderCreate, db: Session = Depends(get_db)):
    """下单，对应系统设计说明书 8.2：POST /api/v1/orders"""
    order = order_service.create_order(db, body)
    return ok(OrderOut.model_validate(order).model_dump())


@router.get("")
def list_orders(pay_status: int | None = None, cook_status: int | None = None, db: Session = Depends(get_db)):
    """订单列表，供管理端按支付/出餐状态筛选"""
    orders = order_service.list_orders(db, pay_status, cook_status)
    return ok([OrderOut.model_validate(o).model_dump() for o in orders])


@router.get("/reviews")
def list_reviews(db: Session = Depends(get_db)):
    """评价列表，供经营分析智能体/管理端统计好评率与差评归因；注册在 /{order_id} 之前避免路由冲突"""
    reviews = order_service.list_reviews(db)
    return ok([ReviewOut.model_validate(r).model_dump() for r in reviews])


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    """订单详情，对应系统设计说明书 8.2：GET /api/v1/orders/{id}"""
    order = order_service.get_order(db, order_id)
    return ok(OrderOut.model_validate(order).model_dump())


@router.post("/{order_id}/status")
def update_order_status(
    order_id: int, pay_status: int | None = None, cook_status: int | None = None, db: Session = Depends(get_db)
):
    """更新支付/出餐状态，供收银台与后厨看板使用"""
    order = order_service.update_status(db, order_id, pay_status, cook_status)
    return ok(OrderOut.model_validate(order).model_dump())


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """删除订单，同时清理关联明细与评价记录"""
    order_service.delete_order(db, order_id)
    return ok(None)


@router.post("/{order_id}/review")
def submit_review(order_id: int, body: ReviewIn, db: Session = Depends(get_db)):
    """顾客提交订单评价（需求文档 3.3、4.4）"""
    review = order_service.submit_review(db, order_id, body)
    return ok(ReviewOut.model_validate(review).model_dump())
