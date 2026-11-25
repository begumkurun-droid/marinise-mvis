# Veri Tabanı Şeması (Section 13)

Kaynak: `backend/app/models.py` (SQLAlchemy 2.0 + GeoAlchemy2). Bu dosya,
kodun insan-okunur özetidir; şema değiştiğinde bu dosya da güncellenmelidir.

## Tablolar

- **users** — RBAC (`UserRole`: super_admin, managing_director,
  business_development, sales_representative, technical_team, read_only)
- **vessels** — IMO/MMSI, tip, boy/genişlik/draft, tonaj, inşa yılı, tersane,
  güncel sefer bilgisi (departure/destination/eta), `is_demo_data` bayrağı
- **vessel_previous_names** — isim geçmişi
- **vessel_positions** — zaman serisi AIS konumu (PostGIS `POINT`), SOG/COG/
  heading/navigational_status, `received_at` indeksli
- **vessel_photos**
- **engine_manufacturers** / **engine_models** — Section 5 öncelikli marka/model
  listesiyle seed edilir; `normalized_key` ile "CAT 3512B" ↔ "Caterpillar 3512 B"
  eşleştirmesi (bkz. `tests/test_engine_normalization.py`)
- **vessel_engines** — kategori (main_engine, auxiliary_engine,
  diesel_generator, emergency_generator, propulsion_system, gearbox),
  güç/RPM/seri no, `verification_status` + `confidence_score` (Section 8)
- **companies** — yalnızca kurumsal/rol-bazlı iletişim alanları (genel,
  teknik, satın alma, operasyon e-postaları) — özel şahıs verisi YOKTUR
  (Section 7 kısıtlaması veri modeli seviyesinde uygulanmıştır)
- **vessel_company_relationships** — gemi↔şirket ilişkisi, rol
  (`CompanyRole`), `is_current` ile geçmiş/güncel ayrımı (Section 7)
- **regions** — geofencing alanları (polygon/rectangle/circle),
  `is_official_territorial_boundary` ile resmî karasuları / operasyonel takip
  alanı ayrımı (Section 4), `is_demo_data`
- **region_events** — giriş/çıkış/yaklaşma/vb. olayları, dedup mantığı
  `app/services/ais_ingest.py::_check_geofence` içinde
- **lead_scores** — Section 10 puanlama + ayrı `data_quality_score`
- **vessel_customer_status** — Section 12 CRM-lite durum makinesi

## Doğrulanmış davranışlar (bu oturumda test edildi)

- Motor marka normalizasyonu: `normalize("3512 B") == normalize("3512B")` ✓
- Geofence dedup: aynı bölgeye art arda konum düşse bile `entered` olayı
  tekrar oluşturulmuyor ✓ (gerçek PostGIS `ST_Contains` sorgusuyla test edildi)
- Lead scoring: CAT ana makine + 30m üzeri yat → 30/100, `low` öncelik
  (demo veriyle, beklenen ağırlıklarla uyumlu) ✓

## Açık noktalar

- Alembic migration yok (bkz. ARCHITECTURE.md)
- `regions` tablosundaki demo poligonlar kaba dikdörtgenlerdir, resmî
  karasuları/Boğaz sınırları değildir — gerçek coğrafi veriyle
  değiştirilmeden bildirim mantığına güvenilmemelidir.
