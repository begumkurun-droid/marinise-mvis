# Mimari (Section 17)

FAZ 0 fizibilite raporunda (bkz. claude.ai projesi > `MARINISE_FAZ0_Fizibilite_Raporu.md`)
yapılan karşılaştırma sonucu önerilen ve bu FAZ 1 iskeletinde uygulanan mimari:

## Bileşenler

| Katman | Teknoloji | Gerekçe |
|---|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind | Section 16/17'nin istediği stack; SSR + statik üretim karışımı |
| Harita | MapLibre GL JS + OpenFreeMap vector tile (`tiles.openfreemap.org`) | Lisans ücreti yok, FAZ0 araştırmasında 2026 itibarıyla hâlâ lider açık kaynak seçenek olarak doğrulandı |
| Backend | FastAPI (Python) | NestJS yerine seçildi: AI Research Agent, veri normalizasyonu ve çoklu-AI-sağlayıcı entegrasyonu Python ekosisteminin güçlü olduğu alanlar (FAZ0 raporu, Bölüm 4) |
| Veri tabanı | PostgreSQL 16 + PostGIS 3.4 | Geospatial+ilişkisel veri için 2026'da hâlâ referans nokta (FAZ0 raporu) |
| Cache/Queue | Redis (+ ileride Celery) | Standart, hafif |
| AIS ingestion | AISStream (ücretsiz WebSocket) → `app/services/ais_ingest.py` | FAZ0 raporunun MVP önerisi |
| Konteynerleştirme | Docker + docker-compose | Yazıldı, bu sandboxta test edilemedi (docker daemon yok) |

## Veri akışı

```
AISStream (ücretsiz WS) ──▶ ais_ingest.py ──▶ vessel_positions (PostGIS) ──▶ /vessels/map/live ──▶ VesselMap.tsx (MapLibre)
                                     │
                                     ▼
                         regions (PostGIS polygon) ──ST_Contains──▶ region_events (dedup'lu)
```

## AI sağlayıcı adaptörü (Section 17)

`app/config.py` içindeki `ai_provider` alanı ("claude" | "openai" | "none") ve
`anthropic_api_key` / `openai_api_key` ortam değişkenleri, gelecekteki AI
Research Agent modülünün tek bir sağlayıcıya bağımlı kalmaması için
hazırlanmıştır. FAZ 5'e kadar `ai_provider=none` ile çalışılır; herhangi bir
ücretli AI çağrısı bu aşamada yapılmaz.

## Bilinçli olarak ertelenen mimari kararlar

- Alembic migration altyapısı yerine şimdilik `Base.metadata.create_all`
  kullanılıyor (`scripts/init_db.py`). Şema stabilize oldukça Alembic'e
  geçilmeli — bkz. PROGRESS.md.
- Celery/BullMQ background job altyapısı henüz kurulmadı; AIS worker şu an
  bağımsız bir process olarak çalışıyor (`python -m app.services.ais_ingest`).
- Rate limiting, 2FA, audit log, otomatik yedekleme (Section 18) FAZ 1
  kapsamında DEĞİL — bkz. `SECURITY.md`.
