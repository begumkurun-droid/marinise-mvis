"""
Auth & RBAC (Section 18: "Role-based access control", "Secure password
management"). JWT-based; two-factor authentication is a stated FAZ-7
production requirement and is intentionally NOT implemented in this FAZ-1
skeleton - flagged in docs/PROGRESS.md rather than silently skipped.
"""
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User, UserRole

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_roles(*allowed: UserRole):
    """Dependency factory: `Depends(require_roles(UserRole.super_admin))`."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed and user.role != UserRole.super_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Yetkisiz işlem")
        return user

    return checker
