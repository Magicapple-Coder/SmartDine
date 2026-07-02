"""平台层数据模型：商户 + 平台管理员（V2.0 新增）"""

from sqlalchemy import BigInteger, Column, DateTime, Integer, SmallInteger, String, func

from app.core.deps import Base


class Merchant(Base):
    """商户（租户）表，对应 sql/00_platform.sql 的 merchant"""

    __tablename__ = "merchant"

    merchant_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    logo = Column(String(255))
    category = Column(String(32))
    address = Column(String(255))
    contact_name = Column(String(32))
    contact_phone = Column(String(20))
    business_hours = Column(String(64))
    tables_count = Column(Integer, nullable=False, default=10)
    status = Column(SmallInteger, nullable=False, default=0)  # 0待审核 1已开通 2已停用 3已注销
    created_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime)


class MerchantAccount(Base):
    """商户管理账号表（V2.0：每个商户的独立登录账号）"""

    __tablename__ = "merchant_account"

    account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False)
    username = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(32))
    role = Column(String(16), nullable=False, default="商家管理员")
    status = Column(SmallInteger, nullable=False, default=1)
    created_at = Column(DateTime, server_default=func.now())


class PlatformAdmin(Base):
    """平台管理员表，对应 sql/00_platform.sql 的 platform_admin"""

    __tablename__ = "platform_admin"

    admin_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(32))
    status = Column(SmallInteger, nullable=False, default=1)
