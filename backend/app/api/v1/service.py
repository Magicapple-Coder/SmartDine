from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.response import ok
from app.schemas.service import ServiceTicketOut, TicketResolve
from app.services import service as service_service

router = APIRouter(prefix="/service/tickets", tags=["客服工单"])


@router.get("")
def list_tickets(status: int | None = None, to_human: int | None = None, db: Session = Depends(get_db)):
    """客服工单队列，供管理端客服处理工作台查看（待人工/已自动/已记录）"""
    tickets = service_service.list_tickets(db, status, to_human)
    return ok([ServiceTicketOut.model_validate(t).model_dump() for t in tickets])


@router.post("/{ticket_id}/resolve")
def resolve_ticket(ticket_id: int, body: TicketResolve, db: Session = Depends(get_db)):
    """人工跟进/处理完成后更新工单状态"""
    ticket = service_service.resolve_ticket(db, ticket_id, body)
    return ok(ServiceTicketOut.model_validate(ticket).model_dump())
