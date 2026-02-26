from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.entities import Role, SlaPolicy, TicketPriority, User


def ensure_defaults(db: Session) -> None:
    if not db.query(User).filter(User.email == "admin@helpdesk.local").first():
        db.add(
            User(
                email="admin@helpdesk.local",
                full_name="Admin",
                password_hash=hash_password("Admin123!"),
                role=Role.ADMIN,
            )
        )

    for priority, first_response, resolve in [
        (TicketPriority.LOW, 240, 2880),
        (TicketPriority.MEDIUM, 120, 1440),
        (TicketPriority.HIGH, 60, 480),
        (TicketPriority.URGENT, 15, 240),
    ]:
        if not db.query(SlaPolicy).filter(SlaPolicy.priority == priority).first():
            db.add(
                SlaPolicy(
                    name=f"default-{priority.value}",
                    priority=priority,
                    first_response_minutes=first_response,
                    resolve_minutes=resolve,
                )
            )

    db.commit()
