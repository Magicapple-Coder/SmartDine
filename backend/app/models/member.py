from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, String, func

from app.core.deps import Base


class Member(Base):
    """平台级会员表，对应 sql/03_other.sql 的 member（V2: 拆分——平台级基本信息，跨商户共享）"""

    __tablename__ = "member"

    member_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(32))
    phone = Column(String(20), nullable=False, unique=True)
    wechat_openid = Column(String(64))
    preferences = Column(String(255))  # 偏好/忌口标签
    allergies = Column(String(255))  # V2.0: 过敏原
    health_goal = Column(String(32))  # V2.0: 健康目标（减脂/增肌/控糖等）
    created_at = Column(DateTime, server_default=func.now())


class MemberMerchant(Base):
    """商户级会员档案表（V2.0 新增——每个商户独立积分/等级/消费记录）"""

    __tablename__ = "member_merchant"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    member_id = Column(BigInteger, nullable=False)
    merchant_id = Column(BigInteger, nullable=False)
    level = Column(String(8), nullable=False, default="普通")  # 黑卡/金卡/银卡/普通
    points = Column(Integer, nullable=False, default=0)
    balance = Column(Numeric(10, 2), nullable=False, default=0)
    visits = Column(Integer, nullable=False, default=0)
    total_spend = Column(Numeric(10, 2), nullable=False, default=0)
    last_visit = Column(DateTime, nullable=True)
    churn_risk_score = Column(Numeric(4, 3))  # V2.0: 流失风险评分
