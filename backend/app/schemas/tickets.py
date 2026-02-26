from datetime import datetime
from pydantic import BaseModel, Field
from app.models.entities import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10)
    category: str = "general"
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    assignee_id: int | None = None
    priority: TicketPriority | None = None


class CommentCreate(BaseModel):
    message: str = Field(min_length=1)
    is_internal: bool = False


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    status: TicketStatus
    priority: TicketPriority
    requester_id: int
    assignee_id: int | None
    first_response_due_at: datetime | None
    resolve_due_at: datetime | None

    class Config:
        from_attributes = True
