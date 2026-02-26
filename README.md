# HelpDesk System (MVP)

Минимальная реализация HelpDesk/Service Desk системы на Python с покрытием ключевой бизнес-логики:

- тикеты, комментарии, статусы, приоритеты;
- роли и разграничение доступа (RBAC);
- SLA-правила и эскалация;
- база знаний;
- CMDB (привязка активов к тикетам);
- аудит действий;
- базовая безопасность (хеширование паролей PBKDF2, блокировка при brute force).

## Структура

- `helpdesk/models.py` — доменные модели и перечисления.
- `helpdesk/security.py` — IAM/безопасность.
- `helpdesk/service.py` — основная бизнес-логика.
- `helpdesk/reporting.py` — отчеты и аналитика.
- `tests/test_helpdesk.py` — unit-тесты.

## Быстрый запуск тестов

```bash
python -m unittest discover -s tests -v
```

## Ограничения MVP

Это backend-domain MVP без веб-интерфейса и без внешнего REST API. Логика спроектирована так,
чтобы ее можно было быстро обернуть в FastAPI/Django/Flask и подключить внешние интеграции
(AD/LDAP, Email, Telegram/Slack, SSO).
