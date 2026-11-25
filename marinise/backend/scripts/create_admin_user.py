"""
Bootstraps the first Super Admin account. There is no public self-registration
endpoint by design (Section 18: RBAC, internal enterprise tool) - every other
user is created by a Super Admin via the User Management screen (FAZ 1
backlog item, not yet built - see docs/PROGRESS.md).

    python -m scripts.create_admin_user admin@marinepower.com "Ad Soyad" "şifre"
"""
import sys

from app.core.security import hash_password
from app.database import SessionLocal
from app.models import User, UserRole


def main() -> None:
    if len(sys.argv) != 4:
        print("Kullanım: python -m scripts.create_admin_user <email> <ad soyad> <şifre>")
        raise SystemExit(1)

    email, full_name, password = sys.argv[1], sys.argv[2], sys.argv[3]
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print(f"Zaten mevcut: {email}")
            return
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=UserRole.super_admin,
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"Super Admin oluşturuldu: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
