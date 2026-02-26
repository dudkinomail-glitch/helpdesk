from __future__ import annotations

from collections import Counter
from datetime import datetime

from helpdesk.models import Ticket, TicketStatus


def tickets_by_status(tickets: list[Ticket]) -> dict[str, int]:
    counter = Counter(ticket.status.value for ticket in tickets)
    return dict(counter)


def resolved_in_period(tickets: list[Ticket], start: datetime, end: datetime) -> int:
    return sum(
        1
        for ticket in tickets
        if ticket.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}
        and start <= ticket.updated_at <= end
    )


def workload_by_assignee(tickets: list[Ticket]) -> dict[int, int]:
    counter = Counter(ticket.assignee_id for ticket in tickets if ticket.assignee_id is not None)
    return dict(counter)
