"""
Seeds: engine manufacturer/model catalog (Section 5 priority list - this is
real reference data, not demo) + a handful of CLEARLY-MARKED demo vessels
and demo regions so the frontend has something to render before a live
AISSTREAM_API_KEY and real geofence polygons are in place.

Every demo row sets is_demo_data=True, per Section 21: "Test verilerini
açıkça Demo Data olarak işaretle."

    python -m scripts.seed_demo_data
"""
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, box

from app.database import SessionLocal
from app.models import (
    EngineCategory,
    EngineManufacturer,
    EngineModel,
    NavigationalStatus,
    Region,
    RegionShape,
    Vessel,
    VesselEngine,
    VesselPosition,
    VesselType,
)

MANUFACTURERS = [
    "Caterpillar",
    "CAT",
    "MASE",
    "Cummins",
    "Onan",
    "Kohler",
    "Rehlko",
    "MTU",
    "MAN",
    "Volvo Penta",
    "Yanmar",
    "Kubota",
    "Perkins",
    "Wärtsilä",
    "Mitsubishi",
    "John Deere",
    "Northern Lights",
    "MAN Energy Solutions",
]

CAT_MODELS = [
    "C4.4", "C7", "C7.1", "C9", "C9.3", "C12", "C18", "C32",
    "3304", "3306", "3406", "3408", "3412", "3508", "3512", "3512B",
    "3512C", "3516", "3516B", "3516C", "C175",
]

MASE_MODELS = ["IS 29", "IS 36", "IS 29/36", "VS 12.8"]


def normalize(model_name: str) -> str:
    return model_name.upper().replace(" ", "").replace("-", "")


def seed_engine_catalog(db) -> dict[str, EngineManufacturer]:
    by_name = {}
    for name in MANUFACTURERS:
        existing = db.query(EngineManufacturer).filter(EngineManufacturer.name == name.upper()).first()
        if existing is None:
            existing = EngineManufacturer(name=name.upper())
            db.add(existing)
            db.flush()
        by_name[name.upper()] = existing

    cat = by_name["CAT"]
    for model in CAT_MODELS:
        key = normalize(model)
        if not db.query(EngineModel).filter(EngineModel.manufacturer_id == cat.id, EngineModel.normalized_key == key).first():
            db.add(EngineModel(manufacturer_id=cat.id, model_name=f"CAT {model}", normalized_key=key))

    mase = by_name["MASE"]
    for model in MASE_MODELS:
        key = normalize(model)
        if not db.query(EngineModel).filter(EngineModel.manufacturer_id == mase.id, EngineModel.normalized_key == key).first():
            db.add(EngineModel(manufacturer_id=mase.id, model_name=f"MASE {model}", normalized_key=key))

    db.flush()
    return by_name


def seed_demo_regions(db) -> None:
    # Coarse placeholder rectangles - NOT the authoritative legal boundary
    # data Section 4 calls for ("Resmî karasuları sınırları güvenilir
    # coğrafi verilerden alınmalı"). Replace before any real notification
    # logic goes live.
    demo_regions = {
        "İstanbul Boğazı (demo)": box(28.90, 40.95, 29.15, 41.25),
        "Çanakkale Boğazı (demo)": box(26.30, 40.00, 26.70, 40.30),
        "Göcek (demo)": box(28.85, 36.70, 28.98, 36.82),
        "Marmaris (demo)": box(28.20, 36.78, 28.35, 36.90),
    }
    for name, geom in demo_regions.items():
        if db.query(Region).filter(Region.name == name).first():
            continue
        db.add(
            Region(
                name=name,
                shape=RegionShape.rectangle,
                geom=from_shape(geom, srid=4326),
                is_official_territorial_boundary=False,
                is_priority=True,
                is_demo_data=True,
            )
        )


def seed_demo_vessels(db, manufacturers: dict[str, EngineManufacturer]) -> None:
    if db.query(Vessel).filter(Vessel.is_demo_data.is_(True)).first():
        return  # already seeded

    demo = Vessel(
        name="DEMO M/Y AEGEAN STAR",
        mmsi="271000001",
        vessel_type=VesselType.motor_yacht,
        flag="Turkey",
        length_m=38.5,
        year_of_build=2016,
        is_demo_data=True,
    )
    db.add(demo)
    db.flush()

    db.add(
        VesselPosition(
            vessel_id=demo.id,
            geom=from_shape(Point(28.95, 36.76), srid=4326),  # Göcek area
            speed_over_ground_kn=6.2,
            course_over_ground_deg=145,
            heading_deg=144,
            navigational_status=NavigationalStatus.under_way_using_engine,
            source="demo",
        )
    )

    cat_model = db.query(EngineModel).filter(EngineModel.normalized_key == normalize("C32")).first()
    db.add(
        VesselEngine(
            vessel_id=demo.id,
            category=EngineCategory.main_engine,
            manufacturer_id=manufacturers["CAT"].id,
            engine_model_id=cat_model.id if cat_model else None,
            engine_model_raw="CAT C32",
            quantity=2,
            rated_power_kw=895,
            verification_status="verified",
            confidence_score=90,
            data_source="Demo Data - manuel giriş",
        )
    )


def main() -> None:
    db = SessionLocal()
    try:
        manufacturers = seed_engine_catalog(db)
        seed_demo_regions(db)
        seed_demo_vessels(db, manufacturers)
        db.commit()
        print("MARINISE: motor kataloğu + demo bölge/gemi verisi yüklendi.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
