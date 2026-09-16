from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers import auth, insights, metrics, reports

app = FastAPI(title="Senus Board Report API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Access is meant to be limited to specific reviewers rather than general internet
# traffic. /health is always exempt so Render's own platform health checks aren't
# blocked. Empty ALLOWED_IPS (the default for local dev/CI) disables this entirely.
@app.middleware("http")
async def restrict_to_allowed_ips(request: Request, call_next):
    if settings.allowed_ips and request.url.path != "/health":
        forwarded_for = request.headers.get("x-forwarded-for")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (
            request.client.host if request.client else None
        )
        if client_ip not in settings.allowed_ips:
            return JSONResponse(status_code=403, content={"detail": "Access restricted"})
    return await call_next(request)

app.include_router(auth.router)
app.include_router(metrics.router)
app.include_router(insights.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}
