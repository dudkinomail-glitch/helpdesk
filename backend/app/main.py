from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import admin, auth, tickets
from app.db.session import Base, engine

app = FastAPI(title="Helpdesk API", version="1.0.0")
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_bucket: dict[str, list[datetime]] = defaultdict(list)
connections: set[WebSocket] = set()


@app.middleware("http")
async def logging_and_rate_limit(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    now = datetime.utcnow()
    rate_bucket[ip] = [t for t in rate_bucket[ip] if now - t < timedelta(minutes=1)]
    if len(rate_bucket[ip]) > 120:
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    rate_bucket[ip].append(now)
    response = await call_next(request)
    response.headers["X-Request-At"] = now.isoformat()
    return response


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


app.include_router(auth.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            for conn in list(connections):
                await conn.send_text(msg)
    except WebSocketDisconnect:
        connections.discard(websocket)


@app.get("/api/health")
def health():
    return {"status": "ok"}
