from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Role(str, Enum):
    USER = "user"
    AGENT = "agent"
    ADMIN = "admin"
    MANAGER = "manager"


class TicketStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_RESPONSE = "waiting_for_response"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class User:
    id: int
    username: str
    full_name: str
    role: Role
    department: str
    password_hash: str
    is_active: bool = True
    two_factor_enabled: bool = False


@dataclass
class Asset:
    id: int
    name: str
    asset_type: str
    owner_department: str


@dataclass
class Comment:
    id: int
    ticket_id: int
    author_id: int
    text: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Ticket:
    id: int
    subject: str
    description: str
    category: str
    priority: Priority
    requester_id: int
    status: TicketStatus = TicketStatus.NEW
    assignee_id: Optional[int] = None
    support_group: str = "L1"
    rejection_reason: Optional[str] = None
    linked_asset_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    due_at: Optional[datetime] = None


@dataclass
class KnowledgeArticle:
    id: int
    title: str
    body: str
    category: str
    author_id: int
    is_published: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SLA:
    id: int
    category: str
    priority: Priority
    resolve_within_hours: int


@dataclass
class AuditEvent:
    id: int
    actor_id: Optional[int]
    action: str
    details: str
    created_at: datetime = field(default_factory=datetime.utcnow)
