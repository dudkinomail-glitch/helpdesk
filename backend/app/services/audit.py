import json
from sqlalchemy.orm import Session

from app.models.entities import AuditLog


def write_audit(db: Session, action: str, actor_id: int | None = None, details: dict | None = None) -> None:
    record = AuditLog(actor_id=actor_id, action=action, details=json.dumps(details or {}))
    db.add(record)
    db.commit()
