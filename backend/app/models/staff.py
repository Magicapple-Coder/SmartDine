from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, SmallInteger, String

from app.core.deps import Base


class Staff(Base):
    """员工表，对应 sql/03_other.sql 的 staff（V2: +merchant_id）"""

    __tablename__ = "staff"

    staff_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    name = Column(String(32), nullable=False)
    role = Column(String(16), nullable=False)  # 店长/收银/后厨/服务员
    account = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    status = Column(SmallInteger, nullable=False, default=1)  # 1在岗 0离职
    weekly_hours = Column(Numeric(5, 1), nullable=False, default=0)


class Schedule(Base):
    """排班表，对应 sql/03_other.sql 的 schedule（V2: +merchant_id）"""

    __tablename__ = "schedule"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    staff_id = Column(BigInteger, ForeignKey("staff.staff_id"), nullable=False)
    date = Column(Date, nullable=False)
    shift = Column(String(8), nullable=False)  # 早/晚/休
