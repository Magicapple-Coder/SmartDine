from sqlalchemy import BigInteger, Column, DateTime, SmallInteger, String, Text, func

from app.core.deps import Base


class ServiceTicket(Base):
    """客服工单表，对应 sql/03_other.sql 的 service_ticket（V2: +merchant_id）"""

    __tablename__ = "service_ticket"

    ticket_id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, nullable=False, default=1)
    member_id = Column(BigInteger, nullable=True)
    channel = Column(String(16))
    content = Column(Text, nullable=False)
    category = Column(String(8))  # 咨询/投诉/建议/预订
    sentiment = Column(String(8))  # 弱/中/强
    draft_reply = Column(Text)
    status = Column(SmallInteger, nullable=False, default=0)  # 0已自动 1待人工 2已记录
    to_human = Column(SmallInteger, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
