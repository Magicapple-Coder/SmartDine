from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.schemas.inventory import (
    IngredientCreate,
    IngredientOut,
    StockLogIn,
    StockLogOut,
    SupplierCreate,
    SupplierOut,
)
from app.services import inventory as inventory_service

router = APIRouter(tags=["库存"])


@router.get("/ingredients")
def list_ingredients(low_stock_only: bool = False, db: Session = Depends(get_db)):
    """食材库存查询；low_stock_only=true 仅返回低于安全阈值的食材（预警列表）"""
    ingredients = inventory_service.list_ingredients(db, low_stock_only)
    return ok([IngredientOut.model_validate(i).model_dump() for i in ingredients])


@router.post("/ingredients")
def create_ingredient(body: IngredientCreate, db: Session = Depends(get_db)):
    ingredient = inventory_service.create_ingredient(db, body)
    return ok(IngredientOut.model_validate(ingredient).model_dump())


@router.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    inventory_service.delete_ingredient(db, ingredient_id)
    return ok(None)


@router.post("/stock-logs")
def record_stock_log(body: StockLogIn, db: Session = Depends(get_db)):
    """入库/出库/损耗登记，自动联动更新食材实时库存"""
    log = inventory_service.record_stock_log(db, body)
    return ok(StockLogOut.model_validate(log).model_dump())


@router.get("/stock-logs")
def list_stock_logs(ingredient_id: int | None = None, db: Session = Depends(get_db)):
    logs = inventory_service.list_stock_logs(db, ingredient_id)
    return ok([StockLogOut.model_validate(l).model_dump() for l in logs])


@router.get("/suppliers")
def list_suppliers(db: Session = Depends(get_db)):
    suppliers = inventory_service.list_suppliers(db)
    return ok([SupplierOut.model_validate(s).model_dump() for s in suppliers])


@router.post("/suppliers")
def create_supplier(body: SupplierCreate, db: Session = Depends(get_db)):
    supplier = inventory_service.create_supplier(db, body)
    return ok(SupplierOut.model_validate(supplier).model_dump())


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    inventory_service.delete_supplier(db, supplier_id)
    return ok(None)
