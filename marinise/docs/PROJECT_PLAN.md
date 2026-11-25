# Proje Planı ve Faz Durumu (Section 20)

| Faz | Durum | Not |
|---|---|---|
| FAZ 0 — Research & Architecture | ✅ Tamamlandı | claude.ai "Vessel Tracker" projesinde `MARINISE_FAZ0_Fizibilite_Raporu.md` |
| FAZ 1 — Core Platform & Live AIS | 🟡 İskelet kuruldu, kullanıcı onayı bekliyor | Bu repo. Bkz. PROGRESS.md "Tamamlanan" / "Açık" listesi |
| FAZ 2 — Geofencing | 🟡 Kısmen (veri modeli + dedup mantığı hazır) | Gerçek poligon verisi ve bildirim kanalları eksik |
| FAZ 3 — Engine Intelligence | 🟡 Şema hazır, veri kaynağı entegrasyonu yok | FAZ0 raporu: jeneratör verisi için kaynak bulunamadı |
| FAZ 4 — Ownership & Management | ⬜ Başlanmadı | Equasis/GISIS entegrasyonu gerekiyor |
| FAZ 5 — AI Research & Lead Generation | ⬜ Başlanmadı | Lead scoring motoru hazır ve test edildi; AI Research Agent yok |
| FAZ 6 — CRM & Reporting | ⬜ Başlanmadı | CRM-lite durum makinesi (vessel_customer_status) şemada mevcut |
| FAZ 7 — Production & UAT | ⬜ Başlanmadı | 2FA, audit log, otomatik yedekleme, UAT dahil değil |

## Sonraki onay noktaları (brief'in kendi kuralı gereği)

- Herhangi bir ücretli API/lisans satın alımı öncesi kullanıcı onayı şart
  (Section 9, 19, 21).
- Production'a deploy öncesi kullanıcı onayı şart (Section 21).

## FAZ 1'in geri kalanı (bu iskelette henüz yok)

- User Management ekranı (şu an yalnızca CLI script ile admin oluşturuluyor)
- Bildirim kanalları (e-posta/Telegram/WhatsApp) — Section 11, FAZ 2 kapsamında
- Alembic migrations
- CI/CD (GitHub Actions) — henüz kurulmadı
