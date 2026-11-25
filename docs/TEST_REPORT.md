# Test ve Durum Raporu — FAZ 1 İskeleti (Section 21)

Tarih: bu geliştirme oturumu. Aşağıdakilerin tümü bu oturumda fiilen
**çalıştırılarak** doğrulandı; hiçbiri varsayım değildir.

## Backend

| Test | Sonuç |
|---|---|
| `pip install -r requirements.txt` | ✅ (psycopg2-binary → psycopg3'e geçildi, Python 3.13 ABI uyumsuzluğu nedeniyle) |
| `pytest` (3 test: lead-priority eşikleri, motor model normalizasyonu) | ✅ 3/3 geçti |
| Tüm modüllerin import edilebilirliği (`app.main`, `ais_ingest`, `scoring`, scripts) | ✅ |
| Gerçek PostgreSQL 16 + PostGIS 3.4 üzerinde `init_db` + `seed_demo_data` | ✅ |
| `create_admin_user` + `/auth/token` ile JWT alma | ✅ (bcrypt/passlib sürüm uyumsuzluğu düzeltildi: `bcrypt==4.0.1`) |
| `/vessels/map/live`, `/dashboard/summary`, `/vessels/{id}` canlı sorgular | ✅ beklenen veriyi döndürdü |
| Lead scoring motoru (`calculate_lead_score`) demo gemi üzerinde | ✅ 30/100, `low` — ağırlıklarla tutarlı |
| Geofence tespiti (`_check_geofence`) gerçek `ST_Contains` sorgusuyla | ✅ giriş olayı 1 kez tetiklendi, ikinci çağrıda mükerrer oluşmadı |

## Frontend

| Test | Sonuç |
|---|---|
| `npm install` | ✅ (Next.js 14.2.15 → 14.2.35'e yükseltildi, bilinen güvenlik açığı nedeniyle) |
| `tsc --noEmit` | ✅ hata yok |
| `next build` (production) | ✅ 7 route başarıyla derlendi |
| `next start` + `/login`, `/`, `/map`, `/vessels` | ✅ hepsi HTTP 200 |

## Test edilmeyenler (dürüstçe işaretlenmiştir)

- `docker compose up` — bu sandbox'ta docker daemon yok
- AISStream'e gerçek bir API anahtarıyla canlı bağlantı — kullanıcının kendi
  ücretsiz anahtarı gerekiyor
- Tarayıcıda gerçek görsel/manuel QA (yalnızca HTTP durum kodları ve derleme
  kontrol edildi)
- Çoklu kullanıcı / RBAC rol bazlı erişim senaryoları (yalnızca super_admin
  ile test edildi)
- Yük/performans testi
