"""
MARINISE MVIS - SQLAlchemy models.

Mirrors docs/DATABASE_SCHEMA.md. Kept in one module for a FAZ-1 skeleton;
split into app/models/*.py once the schema stabilizes (noted in PROGRESS.md).

Every table that can hold placeholder/demo content carries `is_demo_data`,
per Section 21's explicit rule: "Test verilerini açıkça Demo Data olarak
işaretle."
"""
import enum
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def now() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Users & RBAC (Section 18)
# ---------------------------------------------------------------------------
class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    managing_director = "managing_director"
    business_development = "business_development"
    sales_representative = "sales_representative"
    technical_team = "technical_team"
    read_only = "read_only"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.read_only)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


# ---------------------------------------------------------------------------
# Vessels (Section 3)
# ---------------------------------------------------------------------------
class VesselType(str, enum.Enum):
    superyacht = "superyacht"
    motor_yacht = "motor_yacht"
    sailing_yacht = "sailing_yacht"
    commercial_vessel = "commercial_vessel"
    container_vessel = "container_vessel"
    bulk_carrier = "bulk_carrier"
    tanker = "tanker"
    tugboat = "tugboat"
    offshore_vessel = "offshore_vessel"
    passenger_vessel = "passenger_vessel"
    cruise_ship = "cruise_ship"
    fishing_vessel = "fishing_vessel"
    service_vessel = "service_vessel"
    other = "other"


class NavigationalStatus(str, enum.Enum):
    under_way_using_engine = "under_way_using_engine"
    at_anchor = "at_anchor"
    not_under_command = "not_under_command"
    moored = "moored"
    aground = "aground"
    unknown = "unknown"


class Vessel(Base):
    __tablename__ = "vessels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    imo_number: Mapped[str | None] = mapped_column(String(16), unique=True, nullable=True, index=True)
    mmsi: Mapped[str | None] = mapped_column(String(16), unique=True, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    call_sign: Mapped[str | None] = mapped_column(String(32), nullable=True)
    flag: Mapped[str | None] = mapped_column(String(64), nullable=True)
    vessel_type: Mapped[VesselType] = mapped_column(Enum(VesselType), default=VesselType.other)

    length_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    beam_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    draft_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    gross_tonnage: Mapped[float | None] = mapped_column(Float, nullable=True)
    year_of_build: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shipyard: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Latest known voyage snapshot (denormalized for the map/detail card;
    # full history lives in VesselPosition).
    departure_port: Mapped[str | None] = mapped_column(String(255), nullable=True)
    destination_port: Mapped[str | None] = mapped_column(String(255), nullable=True)
    eta: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    previous_names: Mapped[list["VesselPreviousName"]] = relationship(back_populates="vessel")
    positions: Mapped[list["VesselPosition"]] = relationship(back_populates="vessel")
    photos: Mapped[list["VesselPhoto"]] = relationship(back_populates="vessel")
    engines: Mapped[list["VesselEngine"]] = relationship(back_populates="vessel")
    company_links: Mapped[list["VesselCompanyRelationship"]] = relationship(back_populates="vessel")


class VesselPreviousName(Base):
    __tablename__ = "vessel_previous_names"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"))
    name: Mapped[str] = mapped_column(String(255))
    changed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    vessel: Mapped[Vessel] = relationship(back_populates="previous_names")


class VesselPosition(Base):
    """Time-series AIS position. One row per received update."""

    __tablename__ = "vessel_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"), index=True)

    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326))
    speed_over_ground_kn: Mapped[float | None] = mapped_column(Float, nullable=True)
    course_over_ground_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    heading_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    navigational_status: Mapped[NavigationalStatus] = mapped_column(
        Enum(NavigationalStatus), default=NavigationalStatus.unknown
    )
    source: Mapped[str] = mapped_column(String(64), default="aisstream")
    received_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)

    vessel: Mapped[Vessel] = relationship(back_populates="positions")


class VesselPhoto(Base):
    __tablename__ = "vessel_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"))
    url: Mapped[str] = mapped_column(String(1024))
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)

    vessel: Mapped[Vessel] = relationship(back_populates="photos")


# ---------------------------------------------------------------------------
# Engine Intelligence (Section 5) - the module the FAZ-0 report flags as
# hardest to source for commercial vessels, and essentially unsourced for
# generators. Schema is built now so data can be backfilled as sources are
# confirmed.
# ---------------------------------------------------------------------------
class EngineCategory(str, enum.Enum):
    main_engine = "main_engine"
    auxiliary_engine = "auxiliary_engine"
    diesel_generator = "diesel_generator"
    emergency_generator = "emergency_generator"
    propulsion_system = "propulsion_system"
    gearbox = "gearbox"


class VerificationStatus(str, enum.Enum):
    verified = "verified"
    partially_verified = "partially_verified"
    unverified = "unverified"
    conflicting_information = "conflicting_information"
    unknown = "unknown"


class EngineManufacturer(Base):
    """Seeded with Section 5's priority brand list; editable from admin panel."""

    __tablename__ = "engine_manufacturers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)


class EngineModel(Base):
    """`normalized_key` is what matching runs against, so e.g. 'CAT 3512B'
    and 'Caterpillar 3512 B' resolve to the same row (Section 5 requirement)."""

    __tablename__ = "engine_models"
    __table_args__ = (UniqueConstraint("manufacturer_id", "normalized_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("engine_manufacturers.id"))
    model_name: Mapped[str] = mapped_column(String(128))
    normalized_key: Mapped[str] = mapped_column(String(128), index=True)

    manufacturer: Mapped[EngineManufacturer] = relationship()


class VesselEngine(Base):
    __tablename__ = "vessel_engines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"), index=True)
    category: Mapped[EngineCategory] = mapped_column(Enum(EngineCategory))

    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("engine_manufacturers.id"), nullable=True)
    engine_model_id: Mapped[int | None] = mapped_column(ForeignKey("engine_models.id"), nullable=True)
    # Raw string as found in the source, before normalization/matching:
    engine_model_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)

    serial_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    arrangement_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    rated_power_kw: Mapped[float | None] = mapped_column(Float, nullable=True)
    rated_power_hp: Mapped[float | None] = mapped_column(Float, nullable=True)
    rpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    cylinder_configuration: Mapped[str | None] = mapped_column(String(64), nullable=True)
    position: Mapped[str | None] = mapped_column(String(64), nullable=True)
    running_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    installation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_known_maintenance: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_known_overhaul: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    data_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verification_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.unknown
    )
    confidence_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

    vessel: Mapped[Vessel] = relationship(back_populates="engines")
    manufacturer: Mapped[EngineManufacturer | None] = relationship()
    engine_model: Mapped[EngineModel | None] = relationship()


# ---------------------------------------------------------------------------
# Ownership & Management Intelligence (Section 7)
# ---------------------------------------------------------------------------
class CompanyRole(str, enum.Enum):
    registered_owner = "registered_owner"
    beneficial_owner = "beneficial_owner"
    shipowner = "shipowner"
    yacht_owner = "yacht_owner"
    technical_manager = "technical_manager"
    commercial_manager = "commercial_manager"
    ism_manager = "ism_manager"
    yacht_management = "yacht_management"
    fleet_operator = "fleet_operator"
    charter_management = "charter_management"
    ship_agent = "ship_agent"
    fleet_management = "fleet_management"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Corporate/role-based contacts only - never a named private individual's
    # personal data (Section 7: "Özel şahısların gizli iletişim bilgileri
    # araştırılmamalı").
    general_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    technical_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchasing_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operations_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    fleet_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_verification_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class VesselCompanyRelationship(Base):
    __tablename__ = "vessel_company_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    role: Mapped[CompanyRole] = mapped_column(Enum(CompanyRole))
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    vessel: Mapped[Vessel] = relationship(back_populates="company_links")
    company: Mapped[Company] = relationship()


# ---------------------------------------------------------------------------
# Geofencing (Section 4)
# ---------------------------------------------------------------------------
class RegionShape(str, enum.Enum):
    polygon = "polygon"
    rectangle = "rectangle"
    circle = "circle"


class RegionEventType(str, enum.Enum):
    entered = "entered"
    exited = "exited"
    approaching = "approaching"
    arrived_marina = "arrived_marina"
    arrived_shipyard = "arrived_shipyard"
    anchored = "anchored"
    departed = "departed"
    stopped = "stopped"
    target_engine_detected = "target_engine_detected"


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    shape: Mapped[RegionShape] = mapped_column(Enum(RegionShape))
    geom = mapped_column(Geometry(geometry_type="GEOMETRY", srid=4326))

    # Section 4: "Resmî karasuları sınırları ... operasyonel takip
    # alanlarından ayrı tutulmalıdır" - this flag keeps that separation.
    is_official_territorial_boundary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_priority: Mapped[bool] = mapped_column(Boolean, default=True)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False)


class RegionEvent(Base):
    __tablename__ = "region_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"), index=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), index=True)
    event_type: Mapped[RegionEventType] = mapped_column(Enum(RegionEventType))
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=now, index=True)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)

    vessel: Mapped[Vessel] = relationship()
    region: Mapped[Region] = relationship()


# ---------------------------------------------------------------------------
# Lead scoring & CRM-lite (Section 10, Section 12)
# ---------------------------------------------------------------------------
class LeadPriority(str, enum.Enum):
    high = "high"
    medium = "medium"
    potential = "potential"
    low = "low"


class CustomerStatus(str, enum.Enum):
    new_lead = "new_lead"
    under_research = "under_research"
    contact_information_found = "contact_information_found"
    ready_to_contact = "ready_to_contact"
    contacted = "contacted"
    follow_up = "follow_up"
    quotation_opportunity = "quotation_opportunity"
    existing_customer = "existing_customer"
    not_relevant = "not_relevant"


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"), unique=True, index=True)
    score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    priority: Mapped[LeadPriority] = mapped_column(Enum(LeadPriority), default=LeadPriority.low)
    criteria_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    data_quality_score: Mapped[int] = mapped_column(Integer, default=0)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    vessel: Mapped[Vessel] = relationship()


class VesselCustomerStatus(Base):
    __tablename__ = "vessel_customer_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessels.id"), unique=True, index=True)
    status: Mapped[CustomerStatus] = mapped_column(Enum(CustomerStatus), default=CustomerStatus.new_lead)
    assigned_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    vessel: Mapped[Vessel] = relationship()
    assigned_user: Mapped[User | None] = relationship()
