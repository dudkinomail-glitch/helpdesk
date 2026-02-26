from __future__ import annotations

from datetime import datetime, timedelta

from helpdesk.models import (
    Asset,
    AuditEvent,
    Comment,
    KnowledgeArticle,
    Priority,
    Role,
    SLA,
    Ticket,
    TicketStatus,
    User,
)
from helpdesk.security import BruteForceProtector, hash_password, verify_password


class AccessDeniedError(Exception):
    pass


class ValidationError(Exception):
    pass


class NotFoundError(Exception):
    pass


class HelpDeskService:
    def __init__(self) -> None:
        self.users: dict[int, User] = {}
        self.tickets: dict[int, Ticket] = {}
        self.comments: dict[int, Comment] = {}
        self.assets: dict[int, Asset] = {}
        self.articles: dict[int, KnowledgeArticle] = {}
        self.slas: dict[int, SLA] = {}
        self.audit: dict[int, AuditEvent] = {}

        self._user_id = 0
        self._ticket_id = 0
        self._comment_id = 0
        self._asset_id = 0
        self._article_id = 0
        self._sla_id = 0
        self._audit_id = 0

        self.brute_force = BruteForceProtector()

    def _next(self, field: str) -> int:
        current = getattr(self, field)
        nxt = current + 1
        setattr(self, field, nxt)
        return nxt

    def _log(self, actor_id: int | None, action: str, details: str) -> None:
        event_id = self._next("_audit_id")
        self.audit[event_id] = AuditEvent(id=event_id, actor_id=actor_id, action=action, details=details)

    def register_user(self, username: str, full_name: str, role: Role, department: str, password: str) -> User:
        if any(user.username == username for user in self.users.values()):
            raise ValidationError("Username already exists")
        user_id = self._next("_user_id")
        user = User(
            id=user_id,
            username=username,
            full_name=full_name,
            role=role,
            department=department,
            password_hash=hash_password(password),
        )
        self.users[user_id] = user
        self._log(user_id, "user.register", f"Created user {username} with role {role.value}")
        return user

    def authenticate(self, username: str, password: str, now: datetime | None = None) -> User:
        now = now or datetime.utcnow()
        if self.brute_force.is_blocked(username, now=now):
            raise AccessDeniedError("Account is temporarily blocked")

        user = next((u for u in self.users.values() if u.username == username and u.is_active), None)
        if not user or not verify_password(password, user.password_hash):
            self.brute_force.register_failure(username, now=now)
            self._log(None, "auth.failed", f"Failed login for {username}")
            raise AccessDeniedError("Invalid credentials")

        self.brute_force.register_success(username)
        self._log(user.id, "auth.success", "Login successful")
        return user

    def create_ticket(
        self,
        requester: User,
        subject: str,
        description: str,
        category: str,
        priority: Priority,
        asset_id: int | None = None,
    ) -> Ticket:
        if requester.role not in {Role.USER, Role.AGENT, Role.ADMIN, Role.MANAGER}:
            raise AccessDeniedError("Invalid role for ticket creation")
        if asset_id is not None and asset_id not in self.assets:
            raise NotFoundError("Asset not found")

        ticket_id = self._next("_ticket_id")
        due_at = self._calculate_due_at(category, priority)
        ticket = Ticket(
            id=ticket_id,
            subject=subject,
            description=description,
            category=category,
            priority=priority,
            requester_id=requester.id,
            linked_asset_id=asset_id,
            due_at=due_at,
        )
        self.tickets[ticket_id] = ticket
        self._log(requester.id, "ticket.create", f"Created ticket #{ticket_id}")
        return ticket

    def list_user_tickets(self, actor: User, user_id: int | None = None) -> list[Ticket]:
        target_user_id = user_id or actor.id
        if actor.role == Role.USER and target_user_id != actor.id:
            raise AccessDeniedError("User can only see own tickets")
        if actor.role == Role.AGENT:
            target_user = self.users.get(target_user_id)
            if target_user and target_user.department != actor.department:
                raise AccessDeniedError("Agent can't access tickets of another department")
        return [ticket for ticket in self.tickets.values() if ticket.requester_id == target_user_id]

    def add_comment(self, actor: User, ticket_id: int, text: str) -> Comment:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            raise NotFoundError("Ticket not found")
        if actor.role == Role.USER and ticket.requester_id != actor.id:
            raise AccessDeniedError("User can comment only own tickets")

        comment_id = self._next("_comment_id")
        comment = Comment(id=comment_id, ticket_id=ticket_id, author_id=actor.id, text=text)
        self.comments[comment_id] = comment
        ticket.updated_at = datetime.utcnow()
        self._log(actor.id, "ticket.comment", f"Commented on ticket #{ticket_id}")
        return comment

    def assign_to_self(self, actor: User, ticket_id: int) -> Ticket:
        if actor.role not in {Role.AGENT, Role.ADMIN, Role.MANAGER}:
            raise AccessDeniedError("Only support roles can assign tickets")
        ticket = self._get_ticket(ticket_id)
        ticket.assignee_id = actor.id
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.updated_at = datetime.utcnow()
        self._log(actor.id, "ticket.assign", f"Assigned ticket #{ticket_id} to self")
        return ticket

    def change_status(self, actor: User, ticket_id: int, status: TicketStatus, rejection_reason: str | None = None) -> Ticket:
        if actor.role not in {Role.AGENT, Role.ADMIN, Role.MANAGER}:
            raise AccessDeniedError("Only support roles can change status")
        ticket = self._get_ticket(ticket_id)
        ticket.status = status
        ticket.updated_at = datetime.utcnow()
        if status == TicketStatus.REJECTED:
            if not rejection_reason:
                raise ValidationError("Rejection reason is required")
            ticket.rejection_reason = rejection_reason
        self._log(actor.id, "ticket.status", f"Ticket #{ticket_id} -> {status.value}")
        return ticket

    def transfer_ticket(self, actor: User, ticket_id: int, assignee_id: int | None, support_group: str) -> Ticket:
        if actor.role not in {Role.AGENT, Role.ADMIN, Role.MANAGER}:
            raise AccessDeniedError("Only support roles can transfer tickets")
        if assignee_id is not None and assignee_id not in self.users:
            raise NotFoundError("Assignee not found")
        ticket = self._get_ticket(ticket_id)
        ticket.assignee_id = assignee_id
        ticket.support_group = support_group
        ticket.updated_at = datetime.utcnow()
        self._log(actor.id, "ticket.transfer", f"Ticket #{ticket_id} transferred to {support_group}")
        return ticket

    def configure_sla(self, actor: User, category: str, priority: Priority, resolve_within_hours: int) -> SLA:
        if actor.role not in {Role.ADMIN, Role.MANAGER}:
            raise AccessDeniedError("Only manager/admin can configure SLA")
        sla_id = self._next("_sla_id")
        sla = SLA(id=sla_id, category=category, priority=priority, resolve_within_hours=resolve_within_hours)
        self.slas[sla_id] = sla
        self._log(actor.id, "sla.configure", f"SLA set for {category}/{priority.value}")
        return sla

    def escalate_overdue(self, actor: User, now: datetime | None = None) -> list[Ticket]:
        if actor.role not in {Role.AGENT, Role.ADMIN, Role.MANAGER}:
            raise AccessDeniedError("Only support roles can run escalation")
        now = now or datetime.utcnow()
        escalated = []
        for ticket in self.tickets.values():
            if ticket.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED, TicketStatus.REJECTED}:
                continue
            if ticket.due_at and ticket.due_at < now and ticket.priority != Priority.CRITICAL:
                if ticket.priority == Priority.LOW:
                    ticket.priority = Priority.MEDIUM
                elif ticket.priority == Priority.MEDIUM:
                    ticket.priority = Priority.HIGH
                elif ticket.priority == Priority.HIGH:
                    ticket.priority = Priority.CRITICAL
                ticket.updated_at = now
                escalated.append(ticket)
                self._log(actor.id, "ticket.escalate", f"Escalated ticket #{ticket.id}")
        return escalated

    def create_asset(self, actor: User, name: str, asset_type: str, owner_department: str) -> Asset:
        if actor.role not in {Role.ADMIN, Role.MANAGER, Role.AGENT}:
            raise AccessDeniedError("Insufficient permissions for CMDB")
        asset_id = self._next("_asset_id")
        asset = Asset(id=asset_id, name=name, asset_type=asset_type, owner_department=owner_department)
        self.assets[asset_id] = asset
        self._log(actor.id, "asset.create", f"Created asset #{asset_id}")
        return asset

    def create_article(self, actor: User, title: str, body: str, category: str) -> KnowledgeArticle:
        if actor.role not in {Role.AGENT, Role.ADMIN, Role.MANAGER}:
            raise AccessDeniedError("Only support roles can create knowledge articles")
        article_id = self._next("_article_id")
        article = KnowledgeArticle(id=article_id, title=title, body=body, category=category, author_id=actor.id)
        self.articles[article_id] = article
        self._log(actor.id, "kb.create", f"Created KB article #{article_id}")
        return article

    def search_knowledge(self, query: str, category: str | None = None) -> list[KnowledgeArticle]:
        q = query.lower().strip()
        result = []
        for article in self.articles.values():
            if not article.is_published:
                continue
            if category and article.category != category:
                continue
            if q in article.title.lower() or q in article.body.lower():
                result.append(article)
        return result

    def _get_ticket(self, ticket_id: int) -> Ticket:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            raise NotFoundError("Ticket not found")
        return ticket

    def _calculate_due_at(self, category: str, priority: Priority) -> datetime | None:
        matched = next(
            (
                sla
                for sla in self.slas.values()
                if sla.category == category and sla.priority == priority
            ),
            None,
        )
        if not matched:
            return None
        return datetime.utcnow() + timedelta(hours=matched.resolve_within_hours)
