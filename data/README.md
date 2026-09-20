# Struktur Direktori Data Log Book Magang

Direktori ini menyimpan catatan aktivitas harian magang industri dalam format YAML. Setiap berkas mewakili 1 bulan kalender magang (Juli s/d Desember 2026):

```text
data/
├── bulan_01_juli.yaml
├── bulan_02_agustus.yaml
├── bulan_03_september.yaml
├── bulan_04_oktober.yaml
├── bulan_05_november.yaml
└── bulan_06_desember.yaml
```

## Format Berkas

Setiap berkas YAML memiliki struktur berikut:

```yaml
bulan: 7
tahun: 2026
catatan:
  "2026-07-01": "Mengikuti onboarding magang dan setup lingkungan dev."
  "2026-07-02": "Mempelajari spesifikasi REST API backend."
```

## Tips Penggunaan
- Tanggal aktif adalah Senin sampai Sabtu (Minggu libur/otomatis diabaikan).
- Jika ada tanggal yang belum diisi, CLI akan memberikan notifikasi interaktif, atau Anda dapat menggunakan fitur **Batch Auto-Fill** pada Web UI Dashboard.
- Format teks catatan dapat berupa poin-poin ringkas. Fitur ekspansi narasi akan otomatis mengubahnya menjadi kalimat laporan formal berbahasa Indonesia.
