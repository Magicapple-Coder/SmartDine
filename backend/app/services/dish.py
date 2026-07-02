from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import dish as dish_repo
from app.repositories import inventory as inventory_repo
from app.schemas.dish import DishCreate, DishUpdate


def list_available_dishes(db: Session):
    return dish_repo.list_available_dishes(db)


def list_all_dishes(db: Session):
    return dish_repo.list_all_dishes(db)


def _get_or_404(db: Session, dish_id: int):
    dish = dish_repo.get_dish(db, dish_id)
    if dish is None:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return dish


def create_dish(db: Session, body: DishCreate):
    return dish_repo.create_dish(db, **body.model_dump())


def update_dish(db: Session, dish_id: int, body: DishUpdate):
    dish = _get_or_404(db, dish_id)
    return dish_repo.update_dish(db, dish, **body.model_dump())


def set_status(db: Session, dish_id: int, status: int):
    """上架(1)/下架(0)，对应需求文档 3.2 菜品管理"""
    if status not in (0, 1):
        raise HTTPException(status_code=400, detail="status 仅支持 0(下架)/1(上架)")
    dish = _get_or_404(db, dish_id)
    return dish_repo.set_status(db, dish, status)


def delete_dish(db: Session, dish_id: int):
    dish = _get_or_404(db, dish_id)
    inventory_repo.delete_dish_ingredients_by_dish(db, dish_id)
    try:
        dish_repo.delete_dish(db, dish)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="该菜品已有历史订单记录，无法删除，可改为下架")
