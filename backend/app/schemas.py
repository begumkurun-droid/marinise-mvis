"""Pydantic (API) schemas - kept separate from the SQLAlchemy ORM models."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import (
    CompanyRole,
    CustomerStatus,
    EngineCategory,
    LeadPriority,
    NavigationalStatus,
    UserRole,
    VerificationStatus,
    VesselType,
)


class VesselPositionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latitude: float
    longitude: float
    speed_over_ground_kn: float | None = None
    course_over_ground_deg: float | None = None
    heading_deg: float | None = None
    navigational_status: NavigationalStatus
    received_at: datetime


class VesselListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    imo_number: str | None
    mmsi: str | None
    name: str
    vessel_type: VesselType
    flag: str | None
    length_m: float | None
    last_position: VesselPositionOut | None = None


class VesselEngineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: EngineCategory
    manufacturer_name: str | None = None
    engine_model_raw: str | None = None
    rated_power_kw: float | None = None
    rpm: float | None = None
    quantity: int
    verification_status: VerificationStatus
    confidence_score: int


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    role: CompanyRole | None = None
    country: str | None = None
    website: str | None = None
    general_email: str | None = None


class VesselDetail(VesselListItem):
    call_sign: str | None
    beam_m: float | None
    draft_m: float | None
    gross_tonnage: float | None
    year_of_build: int | None
    shipyard: str | None
    departure_port: str | None
    destination_port: str | None
    eta: datetime | None
    engines: list[VesselEngineOut] = []
    companies: list[CompanyOut] = []
    lead_score: int | None = None
    lead_priority: LeadPriority | None = None
    customer_status: CustomerStatus | None = None


class CompanyLinkCreate(BaseModel):
    """
    Section 7/8: the realistic way to populate ownership/management data for
    FAZ 1. Equasis and IMO GISIS both require the researcher's OWN free
    account and neither publishes a documented public API or a confirmed
    automated-access policy (see FAZ0 feasibility report + Section 9's own
    instruction not to bypass access restrictions on platforms that don't
    allow automated collection). So this endpoint does not scrape anything -
    it is where a human (or, later, a properly-licensed data provider)
    records what they found, building MARINISE's own database over time
    (Section 2/13).
    """

    company_name: str
    role: CompanyRole
    country: str | None = None
    website: str | None = None
    general_email: str | None = None
    technical_email: str | None = None
    purchasing_email: str | None = None
    operations_email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    data_source: str = "manuel araştırma"


class ResearchLinks(BaseModel):
    """
    Section 8: "Gerekirse manuel inceleme görevi oluştursun." Entry points
    only - neither site's results can be reliably deep-linked without an
    authenticated session, so the UI shows the vessel's own identifiers for
    the user to paste into the search form themselves.
    """

    imo_number: str | None
    mmsi: str | None
    vessel_name: str
    equasis_url: str
    imo_gisis_url: str
    note: str


class VesselResearchQueueItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    imo_number: str | None
    mmsi: str | None
    vessel_type: VesselType
    customer_status: CustomerStatus | None = None


class DashboardSummary(BaseModel):
    active_tracked_vessels: int
    vessels_in_turkey: int
    vessels_approaching_turkey: int
    cat_engine_vessels: int
    mase_generator_vessels: int
    new_leads_last_7_days: int
    high_priority_leads: int
    data_verification_rate_pct: float
    contact_info_found_rate_pct: float


# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
