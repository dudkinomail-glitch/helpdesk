from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.security import hash_password
from app.db.session import get_db
from app.models.entities import Role, SlaPolicy, User
from app.schemas.admin import SlaPolicyPayload, UserCreateAdmin
from app.services.audit import write_audit

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_roles(Role.ADMIN))):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role} for u in users]


@router.post("/users")
def create_user(payload: UserCreateAdmin, db: Session = Depends(get_db), admin: User = Depends(require_roles(Role.ADMIN))):
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    write_audit(db, "admin.user.create", admin.id, {"user_id": user.id})
    return {"id": user.id, "email": user.email}


@router.put("/sla")
def upsert_sla(payload: SlaPolicyPayload, db: Session = Depends(get_db), admin: User = Depends(require_roles(Role.ADMIN))):
    policy = db.query(SlaPolicy).filter(SlaPolicy.priority == payload.priority).first()
    if not policy:
        policy = SlaPolicy(name=f"default-{payload.priority.value}", priority=payload.priority, first_response_minutes=payload.first_response_minutes, resolve_minutes=payload.resolve_minutes)
        db.add(policy)
    else:
        policy.first_response_minutes = payload.first_response_minutes
        policy.resolve_minutes = payload.resolve_minutes
    db.commit()
    write_audit(db, "admin.sla.update", admin.id, {"priority": payload.priority.value})
    return {"ok": True}
