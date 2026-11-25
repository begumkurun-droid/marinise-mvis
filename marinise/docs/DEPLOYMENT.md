# Deployment (Section 17, 21)

## Durum

Production deployment bu oturumda yapılmadı ve brief'in kendi kuralı gereği
("Kullanıcı onayı olmadan production deployment yapma") yapılmamalıdır.
Bu doküman yalnızca yerel/dev ortam kurulumunu açıklar.

## Docker ile (yazıldı, bu sandbox'ta docker daemon olmadığı için denenmedi)

```bash
cp backend/.env.example backend/.env   # değerleri doldurun
docker compose up --build
```

Servisler: `db` (Postgres+PostGIS), `redis`, `backend` (FastAPI, `init_db`
otomatik çalışır), `ais_worker`, `frontend`.

## Native (bu oturumda fiilen test edilen yol)

Bkz. ana `README.md` "Hızlı başlangıç" bölümü — PostgreSQL 16 + PostGIS 3.4,
Python 3.12+, Node 20 ile adım adım doğrulanmıştır.

## FAZ 7 öncesi eksik olan deployment adımları

- Nginx/Caddy reverse proxy + TLS sertifikası
- GitHub Actions CI/CD pipeline
- Otomatik yedekleme + restore testi
- Cloud sağlayıcı seçimi ve gerçek sunucu kurulumu (Hetzner/DigitalOcean —
  FAZ0 raporunda maliyet tahmini var, gerçek sunucu henüz açılmadı)
