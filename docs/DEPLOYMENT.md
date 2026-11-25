# Deployment (Section 17, 21)

## Durum

Gerçek production deployment (kendi sunucu/domain) bu oturumda yapılmadı ve
brief'in kendi kuralı gereği ("Kullanıcı onayı olmadan production deployment
yapma") yapılmamalıdır. Aşağıdaki "Render.com'a ücretsiz demo kurulumu"
bölümü ise kullanıcının kendi isteğiyle, **sadece deneme/demo amaçlı**,
internetten tıklanabilen bir link elde etmesi için hazırlanmıştır — bir
production kurulumu değildir (bkz. aşağıdaki sınırlamalar).

## Render.com'a ücretsiz demo kurulumu (kullanıcı isteğiyle hazırlandı)

Bu adımları **kullanıcının kendisi** yapmalı — hiçbir hesap/şifre işlemi
Claude tarafından yürütülemez (güvenlik kuralı). Repo kökünde hazır bir
`render.yaml` dosyası var; bu dosya sayesinde tek tıkla 3 servis birden
(veritabanı + backend + frontend) kurulur.

1. **GitHub'a yükleyin**: github.com'da ücretsiz bir hesap açın (yoksa),
   "New repository" ile boş bir repo oluşturun (public), sonra bu projenin
   klasörünü (node_modules, venv, .next, __pycache__ hariç) "Add file >
   Upload files" ile sürükleyip bırakın ve commit edin.
2. **Render'a gidin**: render.com'da ücretsiz hesap açın (e-posta ile veya
   "Sign in with GitHub").
3. **"New +" > "Blueprint"** seçin, az önce oluşturduğunuz GitHub reposunu
   bağlayın. Render, `render.yaml`'ı otomatik okuyup 3 servisi listeler.
4. Devam etmeden önce iki alanı doldurmanız istenecek:
   - Backend servisinde `ADMIN_PASSWORD`: kendi seçeceğiniz bir giriş şifresi.
   - Backend ve frontend'teki `CORS_ORIGINS` / `NEXT_PUBLIC_API_URL`: ilk
     "Apply" sonrası Render her iki servise de otomatik bir adres verir
     (örn. `https://marinise-mvis-frontend.onrender.com`); bu adresleri
     birbirine şu şekilde elle girip "Manual Deploy > Deploy latest commit"
     ile yeniden başlatın:
     - frontend servisi → Environment → `NEXT_PUBLIC_API_URL` = backend'in
       adresi (başına `https://` ekleyerek)
     - backend servisi → Environment → `CORS_ORIGINS` = frontend'in adresi
5. Build bitince (birkaç dakika sürer) frontend servisinin adresi
   tıklanabilir gerçek bir web sitesi olur. Giriş: `ADMIN_EMAIL` (varsayılan
   `admin@marinepower.com`) + yukarıda belirlediğiniz `ADMIN_PASSWORD`.

### Bilinmesi gerekenler (ücretsiz plan sınırlamaları)

- Ücretsiz web servisleri ~15 dakika kullanılmayınca "uyur"; bir sonraki
  ziyarette uyanması 30-60 saniye sürebilir — bu normaldir, hata değildir.
- Ücretsiz Postgres veritabanı 90 gün sonra Render tarafından silinir —
  kalıcı/production kullanım için ücretli plana geçmek gerekir.
- AIS canlı veri worker'ı bu Blueprint'e dahil edilmedi (gerçek
  `AISSTREAM_API_KEY` yoksa anlamsız); sadece demo verisi görünür.
- Bu, FAZ0/FAZ1 raporlarındaki "kullanıcı onayı olmadan production
  deployment yapılmaz" kuralının bir istisnası değil, kullanıcının kendi
  isteğiyle kurduğu bir demo ortamıdır — gerçek production kurulumu hâlâ
  ayrı onay gerektirir.

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
