from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, SmallInteger, String, func

from app.core.deps import Base


class DiningTable(Base):
    """桌台表，对应 sql/03_other.sql 的 dining_table（V2: +merchant_id +qr_code_url）"""

    __tablename__ = "dining_table"

    table_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    no = Column(String(16), nullable=False)
    seats = Column(Integer, nullable=False)
    status = Column(SmallInteger, nullable=False, default=0)  # 0空闲 1就餐中 2已预订 3待清理
    current_order_id = Column(BigInteger, nullable=True)
    qr_code_url = Column(String(255))  # V2.0: 桌台二维码
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Reservation(Base):
    """桌台预订表，对应 sql/03_other.sql 的 reservation（V2: +merchant_id）"""

    __tablename__ = "reservation"

    reservation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    table_id = Column(BigInteger, ForeignKey("dining_table.table_id"), nullable=False)
    member_id = Column(BigInteger, nullable=True)
    contact_name = Column(String(32))
    contact_phone = Column(String(20))
    reserve_time = Column(DateTime, nullable=False)
    guests = Column(Integer, nullable=False, default=1)
    status = Column(SmallInteger, nullable=False, default=0)  # 0待确认 1已确认 2已取消
    created_at = Column(DateTime, server_default=func.now())
