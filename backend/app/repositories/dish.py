from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.models.dish import Dish


def _mid() -> int:
    """获取当前请求的 merchant_id"""
    return current_merchant_id.get() or 1


def list_available_dishes(db: Session) -> list[Dish]:
    """在售菜品列表（V2: 按 merchant_id 过滤）"""
    mid = _mid()
    stmt = select(Dish).where(Dish.status == 1, Dish.merchant_id == mid)
    return list(db.scalars(stmt))


def list_all_dishes(db: Session) -> list[Dish]:
    """全部菜品（含停售，V2: 按 merchant_id 过滤），供管理端菜品管理页使用"""
    mid = _mid()
    return list(db.scalars(select(Dish).where(Dish.merchant_id == mid)))


def get_dish(db: Session, dish_id: int) -> Dish | None:
    mid = _mid()
    return db.query(Dish).filter(Dish.dish_id == dish_id, Dish.merchant_id == mid).first()


def create_dish(db: Session, **kwargs) -> Dish:
    kwargs.setdefault("merchant_id", _mid())
    dish = Dish(**kwargs)
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish


def update_dish(db: Session, dish: Dish, **kwargs) -> Dish:
    for key, value in kwargs.items():
        if value is not None:
            setattr(dish, key, value)
    db.commit()
    db.refresh(dish)
    return dish


def set_status(db: Session, dish: Dish, status: int) -> Dish:
    dish.status = status
    db.commit()
    db.refresh(dish)
    return dish


def delete_dish(db: Session, dish: Dish) -> None:
    db.delete(dish)
    db.commit()
