# Maliyet Analizi (Section 19)

Detaylı analiz ve kaynaklar: claude.ai "Vessel Tracker" projesi,
`MARINISE_FAZ0_Fizibilite_Raporu.md`.

## Özet

| Kalem | Tahmini aylık maliyet |
|---|---|
| Altyapı (VPS + managed DB/Redis veya self-host) | ~$25–60 |
| AIS (MVP, ücretsiz katman) | $0 |
| Engine Intelligence verisi (ücretli, henüz entegre değil) | Datalastic add-on ~€599/ay+ veya Sea-web (teklif bazlı) |
| Kurumsal iletişim (Hunter.io/Apollo.io, henüz entegre değil) | $34–209/ay (Hunter) veya $49–119/kullanıcı/ay (Apollo) |
| AI/LLM API (FAZ 5'e kadar kullanılmıyor) | Henüz $0, `ai_provider=none` |

**Bu FAZ 1 iskeletinin işletme maliyeti şu an $0'dır** — yalnızca ücretsiz
AISStream katmanı kullanılmaktadır, ücretli hiçbir servise abone olunmamıştır.
Yukarıdaki ücretli kalemler yalnızca gelecekteki fazlar için tahmindir ve
hiçbiri kullanıcı onayı olmadan satın alınmamalıdır (Section 9, 19, 21).
