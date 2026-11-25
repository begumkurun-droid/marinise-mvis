"""
Lead Scoring Engine (Section 10).

Mirrors the brief's starting weights exactly; the actual weights are meant
to become editable from an admin panel (Section 10: "Puanlama kriterleri
yönetim panelinden değiştirilebilmelidir") - this module reads them from a
plain dict so that panel can later just rewrite this config instead of code.
"""
from sqlalchemy.orm import Session

from app.models import (
    CompanyRole,
    EngineCategory,
    LeadPriority,
    LeadScore,
    Vessel,
    VesselCompanyRelationship,
    VesselEngine,
    VerificationStatus,
)

DEFAULT_WEIGHTS = {
    "cat_main_engine": 25,
    "cat_generator": 25,
    "mase_generator": 20,
    "in_service_region": 15,
    "verified_management_contact": 10,
    "over_30m": 5,
}


def _priority_for(score: int) -> LeadPriority:
    if score >= 80:
        return LeadPriority.high
    if score >= 60:
        return LeadPriority.medium
    if score >= 40:
        return LeadPriority.potential
    return LeadPriority.low


def calculate_lead_score(db: Session, vessel: Vessel, weights: dict | None = None) -> LeadScore:
    w = weights or DEFAULT_WEIGHTS
    breakdown: dict[str, int] = {}
    total = 0

    engines = (
        db.query(VesselEngine).filter(VesselEngine.vessel_id == vessel.id).all()
    )
    manufacturer_names = {
        e.manufacturer.name.upper() for e in engines if e.manufacturer is not None
    }

    if any(
        e.category == EngineCategory.main_engine and "CAT" in (e.manufacturer.name.upper() if e.manufacturer else "")
        for e in engines
    ) or "CAT" in manufacturer_names or "CATERPILLAR" in manufacturer_names:
        breakdown["cat_main_engine"] = w["cat_main_engine"]

    if any(
        e.category in (EngineCategory.diesel_generator, EngineCategory.auxiliary_engine)
        and e.manufacturer
        and "CAT" in e.manufacturer.name.upper()
        for e in engines
    ):
        breakdown["cat_generator"] = w["cat_generator"]

    if any(
        e.category in (EngineCategory.diesel_generator, EngineCategory.auxiliary_engine)
        and e.manufacturer
        and "MASE" in e.manufacturer.name.upper()
        for e in engines
    ):
        breakdown["mase_generator"] = w["mase_generator"]

    # Section 4/10: being inside a priority service region.
    # (Region-membership lookup is done by the caller via RegionEvent; kept
    # out of this function to avoid a circular query here.)

    verified_mgmt = (
        db.query(VesselCompanyRelationship)
        .filter(
            VesselCompanyRelationship.vessel_id == vessel.id,
            VesselCompanyRelationship.role.in_(
                [CompanyRole.technical_manager, CompanyRole.ism_manager, CompanyRole.yacht_management]
            ),
        )
        .first()
    )
    if verified_mgmt is not None:
        breakdown["verified_management_contact"] = w["verified_management_contact"]

    if vessel.length_m and vessel.length_m > 30:
        breakdown["over_30m"] = w["over_30m"]

    total = min(sum(breakdown.values()), 100)

    # Section 10: "Veri doğruluğu puanı ile ticari müşteri potansiyeli puanı
    # birbirinden ayrı tutulmalıdır" - kept as a separate field, not blended
    # into `score`.
    verified_engines = [e for e in engines if e.verification_status == VerificationStatus.verified]
    data_quality = int(100 * len(verified_engines) / len(engines)) if engines else 0

    existing = db.query(LeadScore).filter(LeadScore.vessel_id == vessel.id).first()
    if existing is None:
        existing = LeadScore(vessel_id=vessel.id)
        db.add(existing)

    existing.score = total
    existing.priority = _priority_for(total)
    existing.criteria_breakdown = breakdown
    existing.data_quality_score = data_quality
    db.flush()
    return existing
