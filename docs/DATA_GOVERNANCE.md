# Veri Yönetişimi (Section 7, 13, 18)

## Uygulanan ilkeler

- **Yalnızca kurumsal/rol-bazlı iletişim verisi saklanır.** `companies`
  tablosunda özel şahıslara ait kişisel veri alanı yoktur (bkz.
  DATABASE_SCHEMA.md). Bu, Section 7'nin "özel şahısların gizli iletişim
  bilgileri araştırılmamalı" kuralının veri modeli seviyesinde uygulanmasıdır.
- **Demo/test verisi her zaman işaretlenir** (`is_demo_data` kolonu, Section 21).
- **Doğrulama durumu her makine/veri kaydında ayrı tutulur**
  (`verification_status`, `confidence_score`) — AI çıkarımı asla doğrulanmış
  gerçek gibi sunulmaz (Section 8).
- **Şirket içi/MARINISE'e özel veri ile dış kaynaklı veri ayrımı** şu an
  `data_source` serbest metin alanıyla takip ediliyor; Section 13'ün istediği
  daha katı ayrım (service history, overhaul geçmişi vb. için ayrı tablolar)
  FAZ 6 kapsamında genişletilmeli.

## KVKK/GDPR

FAZ0 raporunun hukuki notu geçerliliğini koruyor: genel/departman bazlı
kurumsal iletişim verisi standart B2B uygulamasıdır; özel şahıslara ait
kişisel veri toplanmamalıdır. Bu, hukuki tavsiye değildir — gerçek bir
hukuki inceleme FAZ 7 öncesi yapılmalıdır.

## Veri saklama hakları

FAZ0 raporunda belirtildiği gibi, hiçbir AIS/veri sağlayıcısının tam Hizmet
Şartları bu oturumda okunmadı. Üretim ortamında herhangi bir sağlayıcının
verisi uzun süreli saklanmadan önce bu şartlar teyit edilmelidir.
