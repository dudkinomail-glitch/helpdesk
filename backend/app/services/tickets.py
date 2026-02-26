import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.entities import Comment, SlaPolicy, Ticket, TicketHistory, TicketPriority, TicketStatus, User


def _sla_deadlines(db: Session, priority: TicketPriority) -> tuple[datetime | None, datetime | None]:
    policy = db.query(SlaPolicy).filter(SlaPolicy.priority == priority).first()
    if not policy:
        return None, None
    now = datetime.utcnow()
    return now + timedelta(minutes=policy.first_response_minutes), now + timedelta(minutes=policy.resolve_minutes)


def create_ticket(db: Session, requester: User, payload: dict) -> Ticket:
    first_due, resolve_due = _sla_deadlines(db, payload["priority"])
    ticket = Ticket(
        title=payload["title"],
        description=payload["description"],
        category=payload["category"],
        priority=payload["priority"],
        requester_id=requester.id,
        first_response_due_at=first_due,
        resolve_due_at=resolve_due,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    db.add(TicketHistory(ticket_id=ticket.id, actor_id=requester.id, event_type="created", payload="{}"))
    db.commit()
    return ticket


def add_comment(db: Session, ticket: Ticket, actor: User, payload: dict) -> Comment:
    comment = Comment(ticket_id=ticket.id, author_id=actor.id, message=payload["message"], is_internal=payload["is_internal"])
    db.add(comment)
    db.add(TicketHistory(ticket_id=ticket.id, actor_id=actor.id, event_type="comment", payload=json.dumps(payload)))
    if ticket.assignee_id is None and actor.role.value in ["support", "admin"]:
        ticket.assignee_id = actor.id
    db.commit()
    db.refresh(comment)
    return comment


def update_ticket(db: Session, ticket: Ticket, actor: User, changes: dict) -> Ticket:
    for field in ["status", "assignee_id", "priority"]:
        if changes.get(field) is not None:
            setattr(ticket, field, changes[field])
    db.add(TicketHistory(ticket_id=ticket.id, actor_id=actor.id, event_type="updated", payload=json.dumps(changes, default=str)))
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session, actor: User) -> list[Ticket]:
    if actor.role.value == "user":
        return db.query(Ticket).filter(Ticket.requester_id == actor.id).order_by(Ticket.created_at.desc()).all()
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()


def overdue_tickets(db: Session) -> list[Ticket]:
    now = datetime.utcnow()
    return db.query(Ticket).filter(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.PENDING]), Ticket.resolve_due_at < now).all()
