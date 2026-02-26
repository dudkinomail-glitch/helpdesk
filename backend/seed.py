from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import Role, SlaPolicy, TicketPriority, User


def run():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@helpdesk.local").first():
            db.add(User(email="admin@helpdesk.local", full_name="Admin", password_hash=hash_password("Admin123!"), role=Role.ADMIN))
        for p, fr, rs in [
            (TicketPriority.LOW, 240, 2880),
            (TicketPriority.MEDIUM, 120, 1440),
            (TicketPriority.HIGH, 60, 480),
            (TicketPriority.URGENT, 15, 240),
        ]:
            if not db.query(SlaPolicy).filter(SlaPolicy.priority == p).first():
                db.add(SlaPolicy(name=f"default-{p.value}", priority=p, first_response_minutes=fr, resolve_minutes=rs))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print("seed complete")
