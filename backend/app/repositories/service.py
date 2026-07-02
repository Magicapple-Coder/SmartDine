from sqlalchemy.orm import Session

from app.core.tenant import current_merchant_id
from app.models.service import ServiceTicket


def _mid() -> int:
    return current_merchant_id.get() or 1


def create_ticket(db: Session, **kwargs) -> ServiceTicket:
    kwargs.setdefault("merchant_id", _mid())
    ticket = ServiceTicket(**kwargs)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: int) -> ServiceTicket | None:
    mid = _mid()
    return db.query(ServiceTicket).filter(
        ServiceTicket.ticket_id == ticket_id, ServiceTicket.merchant_id == mid
    ).first()


def list_tickets(db: Session, status: int | None = None, to_human: int | None = None):
    mid = _mid()
    query = db.query(ServiceTicket).filter(ServiceTicket.merchant_id == mid)
    if status is not None:
        query = query.filter(ServiceTicket.status == status)
    if to_human is not None:
        query = query.filter(ServiceTicket.to_human == to_human)
    return query.order_by(ServiceTicket.created_at.desc()).all()


def update_status(db: Session, ticket: ServiceTicket, status: int) -> ServiceTicket:
    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return ticket
