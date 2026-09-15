from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, insights, metrics

app = FastAPI(title="Senus Board Report API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(metrics.router)
app.include_router(insights.router)


@app.get("/health")
def health():
    return {"status": "ok"}
