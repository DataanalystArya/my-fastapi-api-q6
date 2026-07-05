import time
import uuid
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

EMAIL = "24f2000456@ds.study.iitm.ac.in"

start_time = time.time()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

logs = deque(maxlen=1000)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())

    http_requests_total.inc()

    response = await call_next(request)

    logs.append({
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id
    })

    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/work")
async def work(n: int):
    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/healthz")
async def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - start_time
    }


@app.get("/logs/tail")
async def tail(limit: int = 10):
    return list(logs)[-limit:]


@app.get("/metrics")
async def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST
    )
