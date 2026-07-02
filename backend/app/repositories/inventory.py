from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.models.inventory import DishIngredient, Ingredient, StockLog, Supplier


def _mid() -> int:
    return current_merchant_id.get() or 1


def list_ingredients(db: Session, low_stock_only: bool = False):
    mid = _mid()
    query = db.query(Ingredient).filter(Ingredient.merchant_id == mid)
    if low_stock_only:
        query = query.filter(Ingredient.stock <= Ingredient.safe_threshold)
    return query.all()


def get_ingredient(db: Session, ingredient_id: int) -> Ingredient | None:
    mid = _mid()
    return db.query(Ingredient).filter(Ingredient.ingredient_id == ingredient_id, Ingredient.merchant_id == mid).first()


def create_ingredient(db: Session, **kwargs) -> Ingredient:
    kwargs.setdefault("merchant_id", _mid())
    ingredient = Ingredient(**kwargs)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


def adjust_stock(db: Session, ingredient: Ingredient, delta) -> Ingredient:
    ingredient.stock = ingredient.stock + delta
    db.commit()
    db.refresh(ingredient)
    return ingredient


def create_stock_log(db: Session, **kwargs) -> StockLog:
    kwargs.setdefault("merchant_id", _mid())
    log = StockLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_stock_logs(db: Session, ingredient_id: int | None = None):
    mid = _mid()
    query = db.query(StockLog).filter(StockLog.merchant_id == mid)
    if ingredient_id is not None:
        query = query.filter(StockLog.ingredient_id == ingredient_id)
    return query.order_by(StockLog.time.desc()).all()


def list_suppliers(db: Session):
    mid = _mid()
    return db.query(Supplier).filter(Supplier.merchant_id == mid).all()


def get_supplier(db: Session, supplier_id: int) -> Supplier | None:
    mid = _mid()
    return db.query(Supplier).filter(Supplier.supplier_id == supplier_id, Supplier.merchant_id == mid).first()


def create_supplier(db: Session, **kwargs) -> Supplier:
    kwargs.setdefault("merchant_id", _mid())
    supplier = Supplier(**kwargs)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def delete_supplier(db: Session, supplier: Supplier) -> None:
    db.delete(supplier)
    db.commit()


def clear_supplier_on_ingredients(db: Session, supplier_id: int) -> None:
    mid = _mid()
    db.query(Ingredient).filter(Ingredient.supplier_id == supplier_id, Ingredient.merchant_id == mid).update({"supplier_id": None})
    db.commit()


def delete_ingredient(db: Session, ingredient: Ingredient) -> None:
    db.delete(ingredient)
    db.commit()


def delete_stock_logs_by_ingredient(db: Session, ingredient_id: int) -> None:
    mid = _mid()
    db.query(StockLog).filter(StockLog.ingredient_id == ingredient_id, StockLog.merchant_id == mid).delete()
    db.commit()


def is_ingredient_used_in_dish(db: Session, ingredient_id: int) -> bool:
    mid = _mid()
    return db.query(DishIngredient).filter(
        DishIngredient.ingredient_id == ingredient_id, DishIngredient.merchant_id == mid
    ).first() is not None


def delete_dish_ingredients_by_dish(db: Session, dish_id: int) -> None:
    mid = _mid()
    db.query(DishIngredient).filter(DishIngredient.dish_id == dish_id, DishIngredient.merchant_id == mid).delete()
    db.commit()
