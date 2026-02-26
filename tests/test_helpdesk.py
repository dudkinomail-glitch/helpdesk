import unittest
from datetime import datetime, timedelta

from helpdesk.models import Priority, Role, TicketStatus
from helpdesk.service import AccessDeniedError, HelpDeskService, ValidationError


class HelpDeskServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = HelpDeskService()
        self.user = self.service.register_user("u1", "User One", Role.USER, "sales", "Secret123!")
        self.agent = self.service.register_user("a1", "Agent One", Role.AGENT, "sales", "Secret123!")
        self.admin = self.service.register_user("admin", "Admin", Role.ADMIN, "it", "Secret123!")

    def test_authenticate_success(self):
        logged = self.service.authenticate("u1", "Secret123!")
        self.assertEqual(logged.id, self.user.id)

    def test_bruteforce_block(self):
        now = datetime.utcnow()
        for _ in range(5):
            with self.assertRaises(AccessDeniedError):
                self.service.authenticate("u1", "bad", now=now)
        with self.assertRaises(AccessDeniedError):
            self.service.authenticate("u1", "Secret123!", now=now + timedelta(minutes=1))

    def test_create_ticket_and_comment(self):
        ticket = self.service.create_ticket(
            requester=self.user,
            subject="Проблема с ПК",
            description="Не включается",
            category="hardware",
            priority=Priority.HIGH,
        )
        self.assertEqual(ticket.status, TicketStatus.NEW)
        comment = self.service.add_comment(self.user, ticket.id, "Добавил фото")
        self.assertEqual(comment.ticket_id, ticket.id)

    def test_agent_workflow(self):
        ticket = self.service.create_ticket(
            requester=self.user,
            subject="Доступ к папке",
            description="Нет прав",
            category="access",
            priority=Priority.MEDIUM,
        )
        self.service.assign_to_self(self.agent, ticket.id)
        self.assertEqual(self.service.tickets[ticket.id].assignee_id, self.agent.id)

        self.service.change_status(self.agent, ticket.id, TicketStatus.WAITING_FOR_RESPONSE)
        self.assertEqual(self.service.tickets[ticket.id].status, TicketStatus.WAITING_FOR_RESPONSE)

    def test_reject_requires_reason(self):
        ticket = self.service.create_ticket(
            requester=self.user,
            subject="test",
            description="test",
            category="general",
            priority=Priority.LOW,
        )
        with self.assertRaises(ValidationError):
            self.service.change_status(self.agent, ticket.id, TicketStatus.REJECTED)

    def test_sla_escalation(self):
        self.service.configure_sla(self.admin, "access", Priority.MEDIUM, resolve_within_hours=1)
        ticket = self.service.create_ticket(
            requester=self.user,
            subject="VPN",
            description="Не подключается",
            category="access",
            priority=Priority.MEDIUM,
        )
        escalated = self.service.escalate_overdue(self.agent, now=datetime.utcnow() + timedelta(hours=2))
        self.assertEqual(len(escalated), 1)
        self.assertEqual(self.service.tickets[ticket.id].priority, Priority.HIGH)

    def test_rbac_user_sees_only_own_tickets(self):
        second = self.service.register_user("u2", "User Two", Role.USER, "sales", "Secret123!")
        self.service.create_ticket(second, "x", "y", "general", Priority.LOW)
        with self.assertRaises(AccessDeniedError):
            self.service.list_user_tickets(self.user, user_id=second.id)

    def test_knowledge_search(self):
        self.service.create_article(self.agent, "Сброс пароля", "Как сбросить пароль", "accounts")
        results = self.service.search_knowledge("пароль")
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
