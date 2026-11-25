from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models import Company, User, VesselCompanyRelationship
from app.schemas import CompanyOut

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(
    name: str | None = Query(default=None, description="Şirket adına göre kısmi arama"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Company Directory (Section 15, menu item 8). Each row here is a company
    MARINISE's own research has recorded (Section 2/13) - never scraped
    automatically, see CompanyLinkCreate's docstring for why.
    """
    q = db.query(Company)
    if name:
        q = q.filter(Company.name.ilike(f"%{name}%"))
    companies = q.order_by(Company.name).all()

    # `role` is really a per-vessel-relationship field, not a company-level
    # one (a company can be technical_manager for one vessel and
    # commercial_manager for another). The directory shows its most recent
    # relationship's role as a representative label.
    out = []
    for c in companies:
        rel = (
            db.query(VesselCompanyRelationship)
            .filter(VesselCompanyRelationship.company_id == c.id)
            .order_by(VesselCompanyRelationship.id.desc())
            .first()
        )
        item = CompanyOut.model_validate(c)
        item.role = rel.role if rel else None
        out.append(item)
    return out
