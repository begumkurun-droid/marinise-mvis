# API Dokümantasyonu (Section 21)

Canlı, otomatik üretilen Swagger/OpenAPI dokümantasyonu backend çalışırken
`/docs` (Swagger UI) ve `/redoc` adreslerinde mevcuttur — bu dosya yalnızca
FAZ 1'de var olan uçların kısa bir özetidir.

| Method | Path | Açıklama | Auth |
|---|---|---|---|
| POST | `/auth/token` | Giriş, JWT döner | Hayır |
| GET | `/auth/me` | Oturum açan kullanıcı | Evet |
| GET | `/vessels` | Filtreli gemi listesi (`vessel_type`, `name`, `engine_manufacturer`) | Evet |
| GET | `/vessels/{id}` | Gemi detay kartı (motor, şirket, lead score) | Evet |
| GET | `/vessels/{id}/track` | Geçmiş konum izi | Evet |
| GET | `/vessels/map/live` | Canlı harita için son konumlar | Evet |
| GET | `/dashboard/summary` | Executive Dashboard rakamları | Evet |
| GET | `/vessels/{id}/research-links` | O gemi için Equasis/IMO GISIS hazır-arama linkleri (IMO/MMSI doldurulmuş not metniyle) | Evet |
| POST | `/vessels/{id}/companies` | Elle bulunan şirket bilgisini (ad, rol, ülke, e-posta, vb.) o gemiye bağlar; şirket yoksa oluşturur, varsa günceller | Evet |
| GET | `/vessels/research/queue` | Henüz hiçbir şirketi kaydedilmemiş gemilerin listesi ("Araştırma Kuyruğu") | Evet |
| GET | `/companies` | Kayıtlı şirketleri isme göre arar/listeler (Company Directory) | Evet |
| GET | `/health` | Servis sağlık kontrolü | Hayır |

## Henüz olmayan uçlar (FAZ 2+)

Geofencing CRUD, lead scoring'i manuel tetikleme, notification tercihleri,
CRM aksiyonları (Section 12) — şema hazır, API katmanı henüz yazılmadı.
Ownership/company uçları artık var (yukarıda), ama yalnızca elle-araştırma
akışı için; otomatik Equasis/GISIS taraması yok (bkz. DATA_PROVIDER_ANALYSIS.md).
