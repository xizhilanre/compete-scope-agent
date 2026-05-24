from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import health
from backend.api.routes import reports, tasks
from backend.config import settings

app = FastAPI(
    title="CompeteScope API",
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(health.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/")
async def root():
    return {"service": "CompeteScope API", "version": "0.2.0"}
