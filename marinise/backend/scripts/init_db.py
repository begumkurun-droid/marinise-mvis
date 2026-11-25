"""
Creates the PostGIS extension + all tables.

    python -m scripts.init_db

A real migration tool (Alembic) should replace this once the schema
stabilizes past FAZ 1 - noted in docs/PROGRESS.md as an open item, not
silently substituted.
"""
from sqlalchemy import text

from app.database import Base, engine
from app import models  # noqa: F401 - import so models register on Base.metadata


def main() -> None:
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print("MARINISE: veri tabanı şeması oluşturuldu (PostGIS etkin).")


if __name__ == "__main__":
    main()
