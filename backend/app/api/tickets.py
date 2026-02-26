from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import Role, Ticket
from app.schemas.tickets import CommentCreate, TicketCreate, TicketOut, TicketUpdate
from app.services.audit import write_audit
from app.services.notifications import push_notification
from app.services.tickets import add_comment, create_ticket, list_tickets, update_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketOut])
def get_tickets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return list_tickets(db, user)


@router.post("", response_model=TicketOut)
def open_ticket(payload: TicketCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ticket = create_ticket(db, user, payload.model_dump())
    write_audit(db, "ticket.created", user.id, {"ticket_id": ticket.id})
    push_notification("tickets", {"event": "ticket_created", "ticket_id": ticket.id})
    return ticket


@router.patch("/{ticket_id}", response_model=TicketOut)
def patch_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SUPPORT, Role.ADMIN)),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Not found")
    updated = update_ticket(db, ticket, user, payload.model_dump())
    write_audit(db, "ticket.updated", user.id, {"ticket_id": ticket_id})
    return updated


@router.post("/{ticket_id}/comments")
def create_comment(ticket_id: int, payload: CommentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Not found")
    comment = add_comment(db, ticket, user, payload.model_dump())
    write_audit(db, "ticket.comment", user.id, {"ticket_id": ticket_id})
    push_notification("tickets", {"event": "comment_created", "ticket_id": ticket_id})
    return {"id": comment.id, "message": comment.message}
