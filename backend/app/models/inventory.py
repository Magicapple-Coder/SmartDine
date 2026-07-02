from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, func

from app.core.deps import Base


class Supplier(Base):
    """供应商表，对应 sql/03_other.sql 的 supplier（V2: +merchant_id +on_time_rate +quality_score +price_stability）"""

    __tablename__ = "supplier"

    supplier_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    name = Column(String(64), nullable=False)
    category = Column(String(32))
    contact = Column(String(32))
    phone = Column(String(20))
    status = Column(SmallInteger, nullable=False, default=1)
    lead_time = Column(Integer, nullable=False, default=1)
    on_time_rate = Column(Numeric(3, 2), default=1.00)  # V2.0: 准时率
    quality_score = Column(Numeric(3, 2), default=1.00)  # V2.0: 品质评分
    price_stability = Column(Numeric(3, 2), default=1.00)  # V2.0: 价格稳定性


class Ingredient(Base):
    """食材表，对应 sql/01_menu_inventory.sql 的 ingredient（V2: +merchant_id）"""

    __tablename__ = "ingredient"

    ingredient_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    supplier_id = Column(BigInteger, ForeignKey("supplier.supplier_id"), nullable=True)
    name = Column(String(32), nullable=False)
    unit = Column(String(8), nullable=False)
    stock = Column(Numeric(10, 3), nullable=False, default=0)
    safe_threshold = Column(Numeric(10, 3), nullable=False, default=0)


class DishIngredient(Base):
    """菜品-食材 BOM 表，对应 sql/01_menu_inventory.sql 的 dish_ingredient（V2: +merchant_id）"""

    __tablename__ = "dish_ingredient"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    dish_id = Column(BigInteger, ForeignKey("dish.dish_id"), nullable=False)
    ingredient_id = Column(BigInteger, ForeignKey("ingredient.ingredient_id"), nullable=False)
    qty_per_serving = Column(Numeric(10, 3), nullable=False)
    unit = Column(String(8), nullable=False)


class StockLog(Base):
    """出入库流水表，对应 sql/01_menu_inventory.sql 的 stock_log（V2: +merchant_id）"""

    __tablename__ = "stock_log"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    ingredient_id = Column(BigInteger, ForeignKey("ingredient.ingredient_id"), nullable=False)
    type = Column(String(8), nullable=False)  # 入库/出库/损耗
    qty = Column(Numeric(10, 3), nullable=False)
    operator = Column(String(32), nullable=False)
    time = Column(DateTime, server_default=func.now())
    remark = Column(String(128))
