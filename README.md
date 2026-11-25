# MARINISE® Vessel Intelligence System (MVIS)

Cloud tabanlı denizcilik istihbarat, canlı gemi takip ve potansiyel müşteri
kazanım platformu. Bu repo, master prompt'un FAZ 0 (fizibilite) onayının
ardından başlatılan **FAZ 1 — Core Platform & Live AIS** iskeletini içerir.

Mevcut durum ve açık noktalar için bkz. [`docs/PROGRESS.md`](docs/PROGRESS.md).
Yol haritası için bkz. [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md).

## Bu oturumda gerçekten doğrulanan şeyler

Aşağıdakiler bu geliştirme oturumunda **çalıştırılarak** test edildi (iddia değil, çalıştırılmış sonuç):

- Yerel PostgreSQL 16 + PostGIS 3.4 üzerinde şema kurulumu (`scripts/init_db.py`)
- Motor kataloğu + demo gemi/bölge verisi yükleme (`scripts/seed_demo_data.py`)
- FastAPI üzerinden JWT auth, `/vessels/map/live`, `/vessels/{id}`, `/dashboard/summary` uçları
- PostGIS tabanlı geofencing (`ST_Contains`) ile bölge giriş tespiti + mükerrer bildirim engelleme
- Lead scoring motorunun Section 10 ağırlıklarına göre doğru puan/öncelik üretmesi
- `pytest` birim testleri (3/3 geçti)
- Next.js 14 + TypeScript + Tailwind frontend'in `tsc --noEmit` ve `next build` ile hatasız derlenmesi
- Üretim modunda (`next start`) tüm sayfaların (login, dashboard, map, vessels) HTTP 200 döndürmesi

**Docker Compose dosyası yazıldı ancak bu sandbox'ta docker daemon bulunmadığı için
`docker compose up` ile uçtan uca denenemedi** — bu, raporlanması gereken açık bir
noktadır (bkz. PROGRESS.md), gizlenmemiştir.

## Dizin yapısı

```
backend/    FastAPI + SQLAlchemy + PostGIS + AIS ingestion worker
frontend/   Next.js (App Router) + MapLibre GL JS canlı harita
docs/       Mimari, veri tabanı, plan, güvenlik, ilerleme dokümanları
docker-compose.yml
```

## Hızlı başlangıç (native, docker olmadan — bu oturumda test edilen yol)

```bash
# 1) PostgreSQL + PostGIS kurulu ve çalışıyor olmalı
cd backend
cp .env.example .env            # DATABASE_URL vb. düzenleyin
pip install -r requirements.txt
python -m scripts.init_db
python -m scripts.seed_demo_data
python -m scripts.create_admin_user admin@firma.com "Ad Soyad" "güçlü-şifre"
uvicorn app.main:app --reload   # http://localhost:8000/docs

# 2) Ayrı bir terminalde AIS worker (ücretsiz AISStream key gerekir)
python -m app.services.ais_ingest

# 3) Frontend
cd ../frontend
cp .env.example .env.local
npm install
npm run dev                     # http://localhost:3000/login
```

## Docker ile (yazıldı, henüz bu ortamda denenmedi)

```bash
docker compose up --build
```

## Önemli notlar

- **Ücretli hiçbir API bu kodda kullanılmaz.** AIS ingestion, AISStream'in
  ücretsiz WebSocket katmanını kullanır; kullanıcı kendi ücretsiz anahtarını
  `.env` dosyasına ekler.
- `is_demo_data=true` olarak işaretli her satır (gemiler, bölgeler) Section 21
  gereği açıkça test verisidir; gerçek veriyle karıştırılmamalıdır.
- Jeneratör marka/model verisi ve ticari gemi ana makine verisi için
  FAZ 0 raporunda tespit edilen kısıtlamalar hâlâ geçerlidir — şema bunlara
  hazır, ancak veri kaynağı entegrasyonu henüz yapılmadı.
