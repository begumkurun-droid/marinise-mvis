from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.shape import to_shape
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from datetime import datetime

from app.models import (
    Company,
    CustomerStatus,
    LeadScore,
    User,
    Vessel,
    VesselCompanyRelationship,
    VesselCustomerStatus,
    VesselEngine,
    VesselPosition,
    VesselType,
)
from app.schemas import (
    CompanyLinkCreate,
    CompanyOut,
    ResearchLinks,
    VesselDetail,
    VesselEngineOut,
    VesselListItem,
    VesselPositionOut,
    VesselResearchQueueItem,
)

router = APIRouter(prefix="/vessels", tags=["vessels"])


def _position_out(position: VesselPosition | None) -> VesselPositionOut | None:
    if position is None or position.geom is None:
        return None
    point = to_shape(position.geom)
    return VesselPositionOut(
        latitude=point.y,
        longitude=point.x,
        speed_over_ground_kn=position.speed_over_ground_kn,
        course_over_ground_deg=position.course_over_ground_deg,
        heading_deg=position.heading_deg,
        navigational_status=position.navigational_status,
        received_at=position.received_at,
    )


def _latest_position(db: Session, vessel_id: int) -> VesselPosition | None:
    return (
        db.query(VesselPosition)
        .filter(VesselPosition.vessel_id == vessel_id)
        .order_by(desc(VesselPosition.received_at))
        .first()
    )


@router.get("", response_model=list[VesselListItem])
def list_vessels(
    vessel_type: VesselType | None = None,
    name: str | None = Query(default=None, description="Ada göre kısmi arama"),
    engine_manufacturer: str | None = Query(default=None, description="Örn. CAT, MASE"),
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Vessel)
    if vessel_type is not None:
        q = q.filter(Vessel.vessel_type == vessel_type)
    if name:
        q = q.filter(Vessel.name.ilike(f"%{name}%"))
    if engine_manufacturer:
        q = q.join(VesselEngine).join(VesselEngine.manufacturer).filter(
            VesselEngine.manufacturer.has(name=engine_manufacturer.upper())
        )

    vessels = q.order_by(Vessel.name).offset(offset).limit(limit).all()
    out = []
    for v in vessels:
        item = VesselListItem.model_validate(v)
        item.last_position = _position_out(_latest_position(db, v.id))
        out.append(item)
    return out


@router.get("/{vessel_id}", response_model=VesselDetail)
def get_vessel(vessel_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    vessel = db.get(Vessel, vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail="Gemi bulunamadı")

    detail = VesselDetail.model_validate(vessel)
    detail.last_position = _position_out(_latest_position(db, vessel.id))

    engines = []
    for e in vessel.engines:
        eo = VesselEngineOut.model_validate(e)
        eo.manufacturer_name = e.manufacturer.name if e.manufacturer else None
        engines.append(eo)
    detail.engines = engines

    companies = []
    for link in vessel.company_links:
        if not link.is_current:
            continue
        co = CompanyOut.model_validate(link.company)
        co.role = link.role
        companies.append(co)
    detail.companies = companies

    lead = db.query(LeadScore).filter(LeadScore.vessel_id == vessel.id).first()
    if lead:
        detail.lead_score = lead.score
        detail.lead_priority = lead.priority

    status_row = db.query(VesselCustomerStatus).filter(VesselCustomerStatus.vessel_id == vessel.id).first()
    detail.customer_status = status_row.status if status_row else CustomerStatus.new_lead

    return detail


@router.get("/{vessel_id}/research-links", response_model=ResearchLinks)
def get_research_links(vessel_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """
    Section 8: manual research helper. Equasis and IMO GISIS both gate their
    ship-particulars results behind a free account; neither publishes a
    documented public API or a confirmed automated-access policy (FAZ0
    report), so this returns entry points + the vessel's own identifiers
    rather than a pre-filled "results" link that would require guessing an
    unverified query format.
    """
    vessel = db.get(Vessel, vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail="Gemi bulunamadı")

    return ResearchLinks(
        imo_number=vessel.imo_number,
        mmsi=vessel.mmsi,
        vessel_name=vessel.name,
        equasis_url="https://www.equasis.org/EquasisWeb/public/HomePage",
        imo_gisis_url="https://gisis.imo.org/Public/Default.aspx",
        note=(
            "Her iki site de kendi ücretsiz hesabınızla giriş gerektiriyor; "
            "sonuç sayfasına doğrudan link verilemiyor (FAZ0 raporu). "
            f"Arama kutusuna bu geminin IMO numarasını yazın: {vessel.imo_number or 'IMO kaydı yok, MMSI: ' + (vessel.mmsi or '-') }"
        ),
    )


@router.post("/{vessel_id}/companies", response_model=CompanyOut)
def add_company_link(
    vessel_id: int,
    payload: CompanyLinkCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Records a manually-researched owner/management company (Section 7) -
    see CompanyLinkCreate's docstring for why this is manual entry rather
    than automated scraping. Reuses an existing Company row by
    case-insensitive name match so the same management company linked to
    multiple vessels doesn't get duplicated (Section 7: "Bir management
    şirketinin yönettiği diğer gemiler de otomatik olarak ilişkilendirilmelidir").
    """
    vessel = db.get(Vessel, vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail="Gemi bulunamadı")

    company = db.query(Company).filter(Company.name.ilike(payload.company_name)).first()
    if company is None:
        company = Company(name=payload.company_name)
        db.add(company)
        db.flush()

    for field in ("country", "website", "general_email", "technical_email", "purchasing_email", "operations_email", "phone", "linkedin_url"):
        value = getattr(payload, field)
        if value:
            setattr(company, field, value)
    company.last_verification_date = datetime.utcnow()
    company.data_sources = {**(company.data_sources or {}), payload.data_source: str(datetime.utcnow())}

    existing_link = (
        db.query(VesselCompanyRelationship)
        .filter(
            VesselCompanyRelationship.vessel_id == vessel_id,
            VesselCompanyRelationship.company_id == company.id,
            VesselCompanyRelationship.role == payload.role,
        )
        .first()
    )
    if existing_link is None:
        db.add(
            VesselCompanyRelationship(
                vessel_id=vessel_id,
                company_id=company.id,
                role=payload.role,
                is_current=True,
            )
        )

    status_row = db.query(VesselCustomerStatus).filter(VesselCustomerStatus.vessel_id == vessel_id).first()
    if status_row is None:
        status_row = VesselCustomerStatus(vessel_id=vessel_id)
        db.add(status_row)
    if status_row.status in (CustomerStatus.new_lead, CustomerStatus.under_research):
        status_row.status = (
            CustomerStatus.contact_information_found if payload.general_email else CustomerStatus.under_research
        )

    db.commit()
    db.refresh(company)
    out = CompanyOut.model_validate(company)
    out.role = payload.role
    return out


@router.get("/research/queue", response_model=list[VesselResearchQueueItem])
def research_queue(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """
    Ownership & Management "to-do" list: vessels with no current company
    link yet. This is the practical, honest substitute for an automatic
    "find the owner" button (Section 7/8) until a licensed data source is
    integrated - see docs/DATA_PROVIDER_ANALYSIS.md.
    """
    linked_vessel_ids = {
        row[0]
        for row in db.query(VesselCompanyRelationship.vessel_id)
        .filter(VesselCompanyRelationship.is_current.is_(True))
        .all()
    }
    vessels = db.query(Vessel).all()
    out = []
    for v in vessels:
        if v.id in linked_vessel_ids:
            continue
        status_row = db.query(VesselCustomerStatus).filter(VesselCustomerStatus.vessel_id == v.id).first()
        item = VesselResearchQueueItem.model_validate(v)
        item.customer_status = status_row.status if status_row else CustomerStatus.new_lead
        out.append(item)
    return out


@router.get("/{vessel_id}/track", response_model=list[VesselPositionOut])
def get_vessel_track(
    vessel_id: int,
    limit: int = Query(default=500, le=5000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Historical voyage track for the vessel detail map (Section 3:
    'Historical position and voyage information')."""
    positions = (
        db.query(VesselPosition)
        .filter(VesselPosition.vessel_id == vessel_id)
        .order_by(desc(VesselPosition.received_at))
        .limit(limit)
        .all()
    )
    return [p for p in (_position_out(pos) for pos in positions) if p is not None]


@router.get("/map/live", response_model=list[VesselListItem])
def live_map(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Latest known position for every vessel - feeds the live map (Section 3)."""
    vessels = db.query(Vessel).all()
    out = []
    for v in vessels:
        pos = _latest_position(db, v.id)
        if pos is None:
            continue
        item = VesselListItem.model_validate(v)
        item.last_position = _position_out(pos)
        out.append(item)
    return out
