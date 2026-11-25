# Güvenlik Durumu (Section 18)

## Bu FAZ 1 iskeletinde VAR olanlar

- Role-based access control (`UserRole` enum + `require_roles` dependency)
- JWT tabanlı oturum, bcrypt ile şifre hash'leme
- Sırlar `.env` üzerinden okunuyor, kodda hard-code edilmiyor
  (`app/config.py`, `.env.example`)
- CORS allow-list (`CORS_ORIGINS`)
- `X-Robots-Tag: noindex, nofollow` (arama motorlarında indekslenmeme şartı)

## Section 18'de istenip bu FAZ 1'de HENÜZ OLMAYANLAR (gizlenmeden listelenmiştir)

- Two-factor authentication
- SSL/TLS terminasyonu (reverse proxy seviyesinde, deployment anında eklenmeli)
- API key encryption (yalnızca ortam değişkeni olarak saklanıyor, ayrı bir
  secret-management servisi yok)
- Rate limiting
- Audit logs
- Otomatik veri tabanı yedekleme + restore testi
- Input validation yalnızca Pydantic şema seviyesinde; ayrıca bir güvenlik
  denetimi/pentest yapılmadı

Bu liste FAZ 7 (Production & UAT) öncesi kapatılması gereken açık maddeler
olarak PROGRESS.md ile senkron tutulmalıdır.
