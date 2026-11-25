# Changelog

## FAZ 1 — İlk iskelet (bu oturum)

### Added
- Backend: FastAPI + SQLAlchemy 2.0 + GeoAlchemy2/PostGIS şeması (vessels,
  positions, engines, companies, regions/geofencing, lead scoring, RBAC)
- JWT auth + RBAC (`require_roles`)
- AISStream (ücretsiz) tabanlı AIS ingestion worker + geofence dedup mantığı
- Lead scoring motoru (Section 10 ağırlıkları)
- `/vessels`, `/vessels/{id}`, `/vessels/{id}/track`, `/vessels/map/live`,
  `/dashboard/summary`, `/auth/*` uçları
- Frontend: Next.js 14 + Tailwind + MapLibre GL JS canlı harita,
  Executive Dashboard, Vessel Database, Vessel Detail, Login, 19 maddelik
  sol menü (Section 15)
- Docker Compose + Dockerfile'lar (backend, frontend)
- `pytest` birim testleri (lead priority eşikleri, motor model normalizasyonu)
- `docs/` altında ARCHITECTURE, DATABASE_SCHEMA, PROJECT_PLAN, SECURITY,
  DEPLOYMENT, API_DOCUMENTATION, DATA_PROVIDER_ANALYSIS, DATA_GOVERNANCE,
  COST_ANALYSIS, TEST_REPORT, UAT_REPORT, PROGRESS, CHANGELOG

### Fixed (bu oturumda karşılaşılan, çözülen sorunlar)
- `psycopg2-binary` Python 3.13 ABI uyumsuzluğu → `psycopg[binary]==3.2.3`'e geçildi
- `passlib`/`bcrypt` sürüm uyumsuzluğu → `bcrypt==4.0.1`'e sabitlendi
- Next.js 14.2.15'teki bilinen güvenlik açığı → 14.2.35'e yükseltildi

### Known gaps
Bkz. `docs/PROGRESS.md`.
