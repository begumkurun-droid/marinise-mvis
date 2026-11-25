"""
AIS ingestion worker (Section 3, Section 4).

Uses AISStream's free WebSocket feed - per docs/FAZ0 feasibility notes this
is the recommended zero-cost starting point for MVP coverage of Turkish
waters / the Eastern Mediterranean. Run as a separate process:

    python -m app.services.ais_ingest

Requires AISSTREAM_API_KEY in .env - a free key the user requests directly
from aisstream.io; no paid service is contacted by this module.

IMPORTANT (flagged, not swept under the rug): this module has not been run
against a live AISStream key in this session - it is written against the
publicly documented message format and needs a first live smoke-test before
FAZ-1 sign-off. See docs/PROGRESS.md "Açık kalan problemler".
"""
import asyncio
import json
import logging
from datetime import datetime

import websockets
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import NavigationalStatus, Region, RegionEvent, RegionEventType, Vessel

logger = logging.getLogger("marinise.ais_ingest")
settings = get_settings()

# Section 4's priority regions, as rough bounding boxes for the AISStream
# subscription filter. These are intentionally coarse (lat/lon rectangles)
# for MVP filtering only - the authoritative polygon-level geofence check
# happens afterwards against the `regions` table (real polygons), per
# Section 4's instruction to keep legal territorial-water boundaries and
# operational tracking areas separate. Marked as demo/placeholder.
TURKEY_EAST_MED_BOUNDING_BOXES = [
    # [[lat_min, lon_min], [lat_max, lon_max]]
    [[35.5, 25.5], [42.5, 36.5]],  # Turkey coast + Aegean + Marmara + Bosphorus + Eastern Med
]

_NAV_STATUS_MAP = {
    0: NavigationalStatus.under_way_using_engine,
    1: NavigationalStatus.at_anchor,
    2: NavigationalStatus.not_under_command,
    5: NavigationalStatus.moored,
    6: NavigationalStatus.aground,
}


def _get_or_create_vessel(db: Session, mmsi: str, name: str | None, imo: str | None) -> Vessel:
    vessel = db.query(Vessel).filter(Vessel.mmsi == mmsi).first()
    if vessel is None:
        vessel = Vessel(mmsi=mmsi, name=name or f"MMSI {mmsi}", imo_number=imo)
        db.add(vessel)
        db.flush()
    elif name and vessel.name != name:
        vessel.name = name
    return vessel


def _check_geofence(db: Session, vessel: Vessel, lon: float, lat: float) -> None:
    """Section 4: detect region entry. Dedup is handled by only firing an
    'entered' event when there wasn't already an un-exited one for the same
    vessel+region (Section 4: 'Tekrarlanan AIS sinyallerinin mükerrer
    bildirim oluşturması engellenmelidir')."""
    point = from_shape(Point(lon, lat), srid=4326)
    regions = db.query(Region).filter(Region.is_priority.is_(True)).all()
    for region in regions:
        inside = db.query(
            db.query(Region)
            .filter(Region.id == region.id)
            .filter(Region.geom.ST_Contains(point))  # type: ignore[attr-defined]
            .exists()
        ).scalar()
        if not inside:
            continue

        already_inside = (
            db.query(RegionEvent)
            .filter(
                RegionEvent.vessel_id == vessel.id,
                RegionEvent.region_id == region.id,
                RegionEvent.event_type == RegionEventType.entered,
            )
            .order_by(RegionEvent.occurred_at.desc())
            .first()
        )
        last_exit = (
            db.query(RegionEvent)
            .filter(
                RegionEvent.vessel_id == vessel.id,
                RegionEvent.region_id == region.id,
                RegionEvent.event_type == RegionEventType.exited,
            )
            .order_by(RegionEvent.occurred_at.desc())
            .first()
        )
        currently_flagged_inside = already_inside is not None and (
            last_exit is None or last_exit.occurred_at < already_inside.occurred_at
        )
        if not currently_flagged_inside:
            db.add(
                RegionEvent(
                    vessel_id=vessel.id,
                    region_id=region.id,
                    event_type=RegionEventType.entered,
                    occurred_at=datetime.utcnow(),
                )
            )


def handle_ais_message(db: Session, raw: dict) -> None:
    """Parses one AISStream JSON message. Format per
    https://aisstream.io/documentation (PositionReport within MessageType)."""
    message_type = raw.get("MessageType")
    metadata = raw.get("MetaData", {})
    mmsi = str(metadata.get("MMSI", "")) or None
    name = metadata.get("ShipName")
    if not mmsi:
        return

    vessel = _get_or_create_vessel(db, mmsi=mmsi, name=name, imo=None)

    if message_type == "PositionReport":
        report = raw["Message"]["PositionReport"]
        lat, lon = report.get("Latitude"), report.get("Longitude")
        if lat is None or lon is None:
            return
        position = Point(lon, lat)

        from app.models import VesselPosition  # local import, avoids top-level cycle

        db.add(
            VesselPosition(
                vessel_id=vessel.id,
                geom=from_shape(position, srid=4326),
                speed_over_ground_kn=report.get("Sog"),
                course_over_ground_deg=report.get("Cog"),
                heading_deg=report.get("TrueHeading"),
                navigational_status=_NAV_STATUS_MAP.get(report.get("NavigationalStatus"), NavigationalStatus.unknown),
                source="aisstream",
            )
        )
        _check_geofence(db, vessel, lon, lat)
        db.commit()


async def run_forever() -> None:
    if not settings.aisstream_api_key:
        logger.error(
            "AISSTREAM_API_KEY not set in .env - get a free key at aisstream.io "
            "and set it before running this worker."
        )
        return

    subscribe_message = {
        "APIKey": settings.aisstream_api_key,
        "BoundingBoxes": TURKEY_EAST_MED_BOUNDING_BOXES,
        "FilterMessageTypes": ["PositionReport"],
    }

    async for ws in websockets.connect(settings.aisstream_ws_url):
        try:
            await ws.send(json.dumps(subscribe_message))
            async for raw_message in ws:
                data = json.loads(raw_message)
                db = SessionLocal()
                try:
                    handle_ais_message(db, data)
                except Exception:  # noqa: BLE001 - keep the worker alive, log and continue
                    logger.exception("AIS message processing failed")
                    db.rollback()
                finally:
                    db.close()
        except websockets.ConnectionClosed:
            logger.warning("AISStream connection closed, reconnecting...")
            continue


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_forever())
