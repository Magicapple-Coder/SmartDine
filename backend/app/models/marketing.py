from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, String, func

from app.core.deps import Base


class Campaign(Base):
    """营销活动表，对应 sql/03_other.sql 的 campaign（V2: +merchant_id）"""

    __tablename__ = "campaign"

    campaign_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    name = Column(String(64), nullable=False)
    type = Column(String(16), nullable=False)  # 优惠券/套餐/限时促销
    rule = Column(String(255))
    period = Column(String(64))
    sold = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())


class Coupon(Base):
    """优惠券表，对应 sql/03_other.sql 的 coupon（V2: +merchant_id）"""

    __tablename__ = "coupon"

    coupon_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    campaign_id = Column(BigInteger, ForeignKey("campaign.campaign_id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    threshold = Column(Numeric(10, 2), nullable=False, default=0)
    claimed = Column(Integer, nullable=False, default=0)
    redeemed = Column(Integer, nullable=False, default=0)
