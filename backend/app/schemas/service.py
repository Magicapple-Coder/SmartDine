from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServiceChatIn(BaseModel):
    message: str
    session_id: str
    conversation_id: str = ""
    member_id: int | None = None
    channel: str = "小程序"


class ServiceChatOut(BaseModel):
    ticket_id: int
    reply: str
    to_human: int
    conversation_id: str = ""


class ServiceTicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: int
    member_id: int | None = None
    channel: str | None = None
    content: str
    category: str | None = None
    sentiment: str | None = None
    draft_reply: str | None = None
    status: int
    to_human: int
    created_at: datetime


class TicketResolve(BaseModel):
    status: int  # 1待人工 2已记录
