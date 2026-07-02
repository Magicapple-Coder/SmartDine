from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.core.security import require_role
from app.schemas.dish import DishCreate, DishOut, DishUpdate
from app.services import dish as dish_service

router = APIRouter(prefix="/dishes", tags=["菜品"])


@router.get("")
def list_dishes(db: Session = Depends(get_db)):
    """在售菜品列表，供用户端菜单浏览与点餐推荐智能体调用"""
    dishes = dish_service.list_available_dishes(db)
    return ok([DishOut.model_validate(d).model_dump() for d in dishes])


@router.get("/all")
def list_all_dishes(db: Session = Depends(get_db), _user: dict = Depends(require_role("商家管理员"))):
    """全部菜品（含停售），供管理端菜品管理页使用"""
    dishes = dish_service.list_all_dishes(db)
    return ok([DishOut.model_validate(d).model_dump() for d in dishes])


@router.post("")
def create_dish(body: DishCreate, db: Session = Depends(get_db), _user: dict = Depends(require_role("商家管理员"))):
    dish = dish_service.create_dish(db, body)
    return ok(DishOut.model_validate(dish).model_dump())


@router.put("/{dish_id}")
def update_dish(
    dish_id: int, body: DishUpdate, db: Session = Depends(get_db), _user: dict = Depends(require_role("商家管理员"))
):
    dish = dish_service.update_dish(db, dish_id, body)
    return ok(DishOut.model_validate(dish).model_dump())


@router.post("/{dish_id}/status")
def set_dish_status(
    dish_id: int, status: int, db: Session = Depends(get_db), _user: dict = Depends(require_role("商家管理员"))
):
    """上架(status=1)/下架(status=0)"""
    dish = dish_service.set_status(db, dish_id, status)
    return ok(DishOut.model_validate(dish).model_dump())


@router.delete("/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db), _user: dict = Depends(require_role("商家管理员"))):
    dish_service.delete_dish(db, dish_id)
    return ok(None)
