"""
Render.com deploy-time bootstrap: creates the PostGIS extension + tables,
seeds the demo catalog/vessel data, and creates the first Super Admin
account from environment variables (so the non-technical user never has
to run a CLI command by hand).

Safe to run on every deploy/restart: every step below checks for existing
data before inserting (see scripts/init_db.py and scripts/seed_demo_data.py
docstrings), so this never duplicates rows.

    python -m scripts.render_bootstrap

Reads ADMIN_EMAIL / ADMIN_PASSWORD / ADMIN_NAME from the environment;
falls back to a fixed demo account if unset, since this is a FAZ 1 demo
deploy, not a production credential (documented in DEPLOYMENT.md).
"""
import os

from app.core.security import hash_password
from app.database import SessionLocal
from app.models import User, UserRole
from scripts import init_db, seed_demo_data


def main() -> None:
    init_db.main()
    seed_demo_data.main()

    email = os.environ.get("ADMIN_EMAIL", "admin@marinepower.com")
    password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
    full_name = os.environ.get("ADMIN_NAME", "Demo Admin")

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print(f"MARINISE: admin zaten mevcut ({email}), atlanıyor.")
            return
        db.add(
            User(
                email=email,
                full_name=full_name,
                hashed_password=hash_password(password),
                role=UserRole.super_admin,
                is_active=True,
            )
        )
        db.commit()
        print(f"MARINISE: Super Admin oluşturuldu -> {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
