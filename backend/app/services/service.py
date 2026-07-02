from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import service as service_repo
from app.schemas.service import ServiceChatIn, TicketResolve

COMPLAINT_KEYWORDS = ("投诉", "退款", "太差", "差评", "不满意")
RESERVATION_KEYWORDS = ("预订", "订座", "订位")


def _classify(message: str) -> tuple[str, str, int]:
    """对顾客消息做关键词分类，得到 (category, sentiment, to_human)。
    Dify 客服处理智能体若未来在 chat-messages 响应中返回结构化分类字段，
    可在此处优先读取该字段，当前以关键词兜底规则保证工单分流可用（需求文档 3.3、5.3）。
    """
    if any(kw in message for kw in COMPLAINT_KEYWORDS):
        return "投诉", "强", 1
    if any(kw in message for kw in RESERVATION_KEYWORDS):
        return "预订", "弱", 0
    return "咨询", "弱", 0


def handle_chat(db: Session, body: ServiceChatIn):
    """关键词分类并回写工单（需求文档 3.3、5.3；系统设计说明书 6.3.5）。
    Dify 智能体已移除，当前仅基于关键词规则做分类分流，自动回复由前端展示预设话术。
    """
    category, sentiment, to_human = _classify(body.message)
    # 按分类生成占位回复，前端可据此展示预设话术
    preset_replies = {"投诉": "您的反馈已记录，客服将尽快与您联系。", "预订": "已收到您的预订需求，我们会尽快确认。"}
    reply = preset_replies.get(category, "感谢您的咨询，我们会尽快回复。")
    ticket = service_repo.create_ticket(
        db,
        member_id=body.member_id,
        channel=body.channel,
        content=body.message,
        category=category,
        sentiment=sentiment,
        draft_reply=reply,
        status=1 if to_human else 0,
        to_human=to_human,
    )
    return ticket, reply, body.conversation_id


def list_tickets(db: Session, status: int | None = None, to_human: int | None = None):
    return service_repo.list_tickets(db, status, to_human)


def resolve_ticket(db: Session, ticket_id: int, body: TicketResolve):
    ticket = service_repo.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="工单不存在")
    return service_repo.update_status(db, ticket, body.status)
