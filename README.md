# Helpdesk Production-Ready Starter

## 1. Архитектура проекта
- **Backend**: FastAPI (REST + OpenAPI `/docs`), SQLAlchemy, JWT (access + refresh), middleware rate limit/logging, WebSocket `/ws/events`.
- **Frontend**: React + TypeScript + Vite + Tailwind, роли User/Support/Admin, optimistic updates, toast, loading states.
- **Data**: PostgreSQL (prod) + миграции SQL-заготовка + seed.
- **Queue**: Redis + worker (`app/workers/sla_worker.py`) для SLA-эскалации.
- **Security**: bcrypt, RBAC guards, audit log table, rate limiting.
- **Infra**: Docker + docker-compose.

## 2. Структура папок
```text
backend/
  app/
    api/           # auth, tickets, admin endpoints
    core/          # config/security
    db/            # engine/session
    models/        # ORM entities
    schemas/       # DTO/validation
    services/      # business logic
    workers/       # background jobs
  migrations/
  tests/
frontend/
  src/
    api/ components/ context/ pages/ types/
docker-compose.yml
.env.example
```

## 3. Схема БД
- `users` (email, password_hash, role)
- `tickets` (status, priority, requester, assignee, SLA дедлайны)
- `comments` (публичные/внутренние)
- `ticket_history` (история изменений)
- `sla_policies` (first response/resolve по priority)
- `audit_logs` (критические действия)

## 4. Backend код
- `POST /api/auth/register`, `POST /api/auth/login`
- `GET/POST/PATCH /api/tickets`, `POST /api/tickets/{id}/comments`
- `GET/POST /api/admin/users`, `PUT /api/admin/sla`
- `GET /api/health`, WebSocket `/ws/events`

## 5. Frontend код
- `/login`: email/password auth
- `/`: список и создание тикетов
- `/admin`: управление пользователями (для админа)
- Realtime refresh через WebSocket, toast-уведомления, responsive layout
- Frontend по умолчанию ходит в backend на том же хосте браузера (`http://<current-host>:8000`), чтобы корректно работать на VM без `localhost`-ловушки.

## 6. Docker
```bash
docker compose up --build
```
Services: `db`, `redis`, `backend:8000`, `frontend:5173`.

## 7. Инструкции запуска
### Локально backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Локально frontend
```bash
cd frontend
npm install
npm run dev
```

### Scripts (dev/prod)
- Dev: `docker compose up --build`
- Prod baseline: `docker compose -f docker-compose.yml up -d --build`

Default admin:
- `admin@helpdesk.local / Admin123!`
- Создаётся автоматически при старте API (или вручную через `python seed.py`).
