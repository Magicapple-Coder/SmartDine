from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import inventory as inventory_repo
from app.schemas.inventory import IngredientCreate, StockLogIn, SupplierCreate

STOCK_DELTA_SIGN = {"入库": 1, "出库": -1, "损耗": -1}


def list_ingredients(db: Session, low_stock_only: bool = False):
    return inventory_repo.list_ingredients(db, low_stock_only)


def create_ingredient(db: Session, body: IngredientCreate):
    return inventory_repo.create_ingredient(db, **body.model_dump())


def _get_ingredient_or_404(db: Session, ingredient_id: int):
    ingredient = inventory_repo.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="食材不存在")
    return ingredient


def delete_ingredient(db: Session, ingredient_id: int):
    ingredient = _get_ingredient_or_404(db, ingredient_id)
    if inventory_repo.is_ingredient_used_in_dish(db, ingredient_id):
        raise HTTPException(status_code=400, detail="该食材已被菜品配方使用，无法删除")
    inventory_repo.delete_stock_logs_by_ingredient(db, ingredient_id)
    inventory_repo.delete_ingredient(db, ingredient)


def record_stock_log(db: Session, body: StockLogIn):
    """登记出入库/损耗流水，并联动更新食材实时库存（需求文档 3.6）"""
    ingredient = inventory_repo.get_ingredient(db, body.ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="食材不存在")
    sign = STOCK_DELTA_SIGN.get(body.type)
    if sign is None:
        raise HTTPException(status_code=400, detail="出入库类型仅支持 入库/出库/损耗")
    delta = Decimal(sign) * body.qty
    if sign < 0 and ingredient.stock + delta < 0:
        raise HTTPException(status_code=400, detail="库存不足，无法出库/登记损耗")
    inventory_repo.adjust_stock(db, ingredient, delta)
    return inventory_repo.create_stock_log(db, **body.model_dump())


def list_stock_logs(db: Session, ingredient_id: int | None = None):
    return inventory_repo.list_stock_logs(db, ingredient_id)


def list_suppliers(db: Session):
    return inventory_repo.list_suppliers(db)


def create_supplier(db: Session, body: SupplierCreate):
    return inventory_repo.create_supplier(db, **body.model_dump())


def delete_supplier(db: Session, supplier_id: int):
    supplier = inventory_repo.get_supplier(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    inventory_repo.clear_supplier_on_ingredients(db, supplier_id)
    inventory_repo.delete_supplier(db, supplier)
