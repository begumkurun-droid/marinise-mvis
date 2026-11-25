from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, companies, dashboard, vessels

settings = get_settings()

app = FastAPI(
    title="MARINISE Vessel Intelligence System API",
    version="0.1.0-faz1",
    description=(
        "FAZ 1 skeleton API. Section 21 note: this is enterprise-scaffolding "
        "in progress, not yet FAZ-7 production-ready - see docs/PROGRESS.md."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vessels.router)
app.include_router(companies.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}
