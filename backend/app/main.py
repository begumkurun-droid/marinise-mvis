import asyncio
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, companies, dashboard, vessels

# Render only shows what actually reaches stdout. Python's root logger
# defaults to WARNING, so without this, our own INFO lines (and any
# exception raised inside the AIS background task) are silently dropped
# instead of showing up in the Render log viewer.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)

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
    task = asyncio.create_task(run_forever())

    def _log_if_failed(finished_task: "asyncio.Task[None]") -> None:
        # A background task's exception is otherwise swallowed until the
        # task is garbage-collected - log it immediately so a bad/expired
        # key or a connection error shows up in Render's log viewer.
        if finished_task.cancelled():
            return
        exc = finished_task.exception()
        if exc is not None:
            logger.error("AIS ingestion task stopped with an error: %r", exc)

    task.add_done_callback(_log_if_failed)
