from pydantic import BaseModel, EmailStr
from app.models.entities import Role, TicketPriority


class UserCreateAdmin(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Role


class SlaPolicyPayload(BaseModel):
    priority: TicketPriority
    first_response_minutes: int
    resolve_minutes: int
