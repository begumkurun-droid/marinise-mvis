# Veri Sağlayıcı Analizi (Section 9)

Tam karşılaştırmalı analiz claude.ai "Vessel Tracker" projesindeki
`MARINISE_FAZ0_Fizibilite_Raporu.md` belgesindedir (AIS, Engine Intelligence,
Ownership/Management/Contact bölümleri, kaynak linkleriyle). Bu dosya o
raporun FAZ 1 karar özetidir:

- **AIS:** AISStream (ücretsiz) FAZ 1'de entegre edildi (`app/services/ais_ingest.py`).
  AISHub ikinci seçenek olarak değerlendirilebilir.
- **Engine Intelligence:** Henüz hiçbir harici kaynak entegre edilmedi — şema
  hazır (bkz. DATABASE_SCHEMA.md), veri girişi şu an yalnızca demo/manuel.
  Jeneratör verisi için FAZ0 raporunda hiçbir güvenilir kaynak bulunamadığı
  unutulmamalı.
- **Ownership/Management:** Tam otomatik Equasis/IMO GISIS entegrasyonu (ileride
  mümkün olursa) FAZ 4 kapsamında planlanıyor, henüz yapılmadı. Bu sırada FAZ 1'e
  **elle-araştırma destekli** bir ara çözüm eklendi (`/vessels/{id}/research-links`,
  `/vessels/{id}/companies`, `/vessels/research/queue`, `/companies`; frontend'de
  gemi detay sayfası, `/ownership` ve `/companies`). Gerekçe: her iki platform da
  (a) resmi, genel kullanıma açık bir API sunmuyor, (b) gerçek veriye erişim
  kişisel/ücretsiz hesap girişi gerektiriyor, (c) otomatik toplamaya izin verip
  vermediği doğrulanamadı. Brief'in kendi Section 9 kuralı — API'si olmayan veya
  otomatik toplamaya izin vermeyen platformların erişim kısıtlarının aşılmaması —
  bu yüzden otomatik scraping'i dışladı. Bunun yerine kullanıcı (iş geliştirme
  ekibi) geminin IMO/MMSI'si önceden doldurulmuş linklerle Equasis/GISIS'te elle
  arama yapıyor, bulduğunu bir formla kaydediyor; bu da zamanla MARINISE'ın kendi
  şirket veri tabanını (Section 2'nin hedefi) oluşturuyor. "Araştırma Kuyruğu"
  sayfası hangi gemilerin hâlâ araştırılması gerektiğini otomatik listeliyor.
- **Kurumsal iletişim (Hunter.io/Apollo.io):** Entegre edilmedi; FAZ0
  raporundaki "denizcilik sektörü kapsaması doğrulanmadı" uyarısı hâlâ geçerli.

Herhangi bir ücretli sağlayıcı aboneliği, FAZ0 raporunun "doğrulanmadan bütçe
taahhüt edilmemeli" listesindeki maddeler teyit edilmeden başlatılmamalıdır.
