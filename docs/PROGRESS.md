# İlerleme ve Açık Problemler (Section 21: "Açık kalan problemleri raporla")

## Tamamlanan (FAZ 1 iskeleti, çalıştırılarak doğrulandı — bkz. TEST_REPORT.md)

- Veri tabanı şeması (12 tablo), PostGIS geometrileriyle
- AIS ingestion worker (AISStream, ücretsiz) + geofence giriş tespiti + dedup
- Lead scoring motoru, Section 10 ağırlıklarıyla
- JWT auth + RBAC
- REST API: canlı harita, dashboard, gemi listesi/detay/iz
- Next.js frontend: login, dashboard, canlı harita, gemi veri tabanı, gemi
  detay, 19 maddelik sol menü (henüz yapılmayan modüller "yakında" sayfasına
  gidiyor — ölü link bırakılmadı, Section 21)
- **Ownership & Management ("gemi sahibini bulma") — elle-araştırma destekli
  akış (Section 7/8)**: gemi detayında Equasis + IMO GISIS'e doğrudan,
  geminin IMO/MMSI numarası önceden yazılı linkler; bulunan şirket bilgisini
  (ad, rol, ülke, web sitesi, e-postalar) kaydeden form; şirket kaydı
  olmayan gemileri listeleyen "Araştırma Kuyruğu" sayfası (`/ownership`);
  tüm kayıtlı şirketleri arayıp listeleyen "Company Directory" sayfası
  (`/companies`). Otomatik/robotik arama **bilerek yapılmadı** — Equasis ve
  IMO GISIS'in resmi genel API'si yok ve her ikisi de kişisel ücretsiz hesap
  girişi istiyor; brief'in kendi kuralı (Section 9) otomasyon izni olmayan
  platformların bypass edilmesini yasaklıyor. Bu yüzden "tek tıkla otomatik
  bulma" yerine hızlı-arama + kaydet akışı kuruldu. Uçtan uca gerçek
  Postgres+API ile test edildi: gemi önce kuyrukta → link verildi → şirket
  kaydedildi → gemi kuyruktan düştü → şirket hem gemi detayında hem Company
  Directory'de göründü.
- Docker Compose + Dockerfile'lar
- 14 doküman (README + docs/*)

## Açık problemler (sıralı öncelik)

1. **AISStream canlı bağlantısı hiç test edilmedi** — kullanıcının kendi
   ücretsiz API anahtarını alıp `.env`'e eklemesi, sonra worker'ı gerçek
   trafikle çalıştırıp doğrulaması gerekiyor.
2. **Docker Compose stack'i hiç `up` edilmedi** — bu sandboxta docker daemon
   yok. Kullanıcı kendi ortamında `docker compose up --build` çalıştırıp
   sonucu bildirmeli.
3. **Jeneratör verisi** için hâlâ hiçbir kaynak yok (FAZ0 raporu) — şema hazır,
   veri girişi manuel/AI-research'e kalıyor.
4. **Demo geofencing poligonları kaba dikdörtgenlerdir**, gerçek karasuları/
   Boğaz sınırı verisi değildir — gerçek bildirim mantığına güvenilmeden önce
   gerçek coğrafi veriyle değiştirilmelidir (Section 4).
5. **Alembic migration yok** — şema `create_all` ile kuruluyor; şema
   değiştikçe elle senkronize edilmesi gerekiyor.
6. **User Management ekranı yok** — kullanıcılar şu an yalnızca
   `scripts/create_admin_user.py` CLI scripti ile oluşturuluyor.
7. **Section 18'in bir kısmı eksik**: 2FA, rate limiting, audit log, otomatik
   yedekleme (bkz. SECURITY.md) — FAZ 7 öncesi kapatılmalı.
8. **Engine/Contact veri kaynakları henüz entegre değil; Ownership artık
   elle-araştırma akışıyla destekleniyor ama otomatik değil** — FAZ0
   raporundaki "doğrulanmadı" işaretli noktalar (Equasis/GISIS resmi API
   yokluğu) hâlâ doğrulanmadı; otomatik şirket/iletişim bulma için ücretli
   bir sağlayıcı (örn. Datalastic, Hunter.io) gerekecek ve bu kullanıcı
   onayı ister.
9. **CI/CD (GitHub Actions) kurulmadı.**

## Onay bekleyen kararlar

- Yukarıdaki açık problemlerden hangilerine öncelik verileceği
- Herhangi bir ücretli veri sağlayıcısına (Datalastic, Sea-web, Hunter.io,
  Apollo.io) abone olunup olunmayacağı — brief'in kendi kuralı gereği bu,
  kullanıcı onayı gerektirir.
