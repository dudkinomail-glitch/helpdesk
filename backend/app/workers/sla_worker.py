from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.tickets import overdue_tickets
from app.services.notifications import push_notification


def run_sla_escalation() -> int:
    db: Session = SessionLocal()
    try:
        tickets = overdue_tickets(db)
        for t in tickets:
            push_notification("tickets", {"event": "sla_overdue", "ticket_id": t.id})
        return len(tickets)
    finally:
        db.close()


if __name__ == "__main__":
    print({"overdue": run_sla_escalation()})
