import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, companies, dashboard, vessels

settings = get_settings()
logger = logging.getLogger("marinise.main")

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


@app.on_event("startup")
async def _start_ais_ingestion_if_configured() -> None:
    # No separate worker process/paid instance on the free plan: when a key
    # is present, the AIS listener runs as a background task inside this
    # same API process (Section 3). It pauses whenever the free instance
    # spins down from inactivity - documented in docs/DEPLOYMENT.md, not a
    # silent limitation.
    if not settings.aisstream_api_key:
        logger.info("AISSTREAM_API_KEY not set - skipping live AIS ingestion (demo data only).")
        return
    from app.services.ais_ingest import run_forever

    logger.info("AISSTREAM_API_KEY set - starting live AIS ingestion background task.")
    asyncio.create_task(run_forever())
