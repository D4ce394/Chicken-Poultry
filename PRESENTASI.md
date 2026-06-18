# Checklist Presentasi — AI-FRSS Dashboard

## Arsitektur Sistem

| Komponen | Platform | URL |
|----------|----------|-----|
| Frontend (fe) | Vercel | URL Vercel kamu |
| Backend 1 / API utama (be1) | Railway | URL Railway kamu |
| Backend 2 / AI + Firebase (be2) | Hugging Face Spaces | `https://d4ce-chicken-poultry.hf.space` |
| Backend 3 / RFID Absensi (be3) | — | Belum di-deploy |

---

## H-1 Sebelum Presentasi

### 1. Cek be1 (Railway) — Backend Utama
- [ ] Buka URL Railway → pastikan tidak 502/crash
- [ ] Login di dashboard dengan `admin@admin.com` / `Admin123!`
- [ ] Kalau gagal login, cek Railway Logs: kemungkinan SQLite belum sync

### 2. Cek be2 (Hugging Face Spaces)
- [ ] Buka `https://d4ce-chicken-poultry.hf.space` di browser
- [ ] Pastikan statusnya **Running** (bukan Building/Sleeping/Error)
- [ ] Cek Settings → Repository Secrets → sudah ada `FIREBASE_SERVICE_ACCOUNT_BASE64`
- [ ] Kalau belum ada secret, Firebase tidak akan konek → data ayam tidak muncul

### 3. Cek Frontend (Vercel)
- [ ] Settings → Environment Variables sudah ada:
  - `PUBLIC_API_URL` = URL Railway be1 + `/api`
  - `PUBLIC_BE2_URL` = `https://d4ce-chicken-poultry.hf.space`
- [ ] Setelah set env var, **harus Redeploy** (bukan hanya save)
- [ ] Coba login dari URL Vercel → masuk dashboard → data muncul

### 4. Cek Data Firebase
- [ ] Buka Firebase Console → project `rfid-de0fd`
- [ ] Realtime Database → pastikan ada node `chicken_counter`
- [ ] Kalau kosong, data hitungan ayam tidak akan tampil (normal kalau belum ada sesi)

---

## Saat Presentasi

### Urutan Demo yang Aman
1. **Login** → `admin@admin.com` / `Admin123!`
2. **Dashboard** → tampilkan overview
3. **Halaman Chicken Counting** → data sesi & grafik
4. **Halaman Rekap** → ringkasan harian/bulanan
5. **Halaman Konfigurasi** → tunjukkan upload model & pengaturan

### Yang JANGAN Dilakukan Saat Demo
- ❌ Jangan coba fitur **Live Counting dari kamera** — CPU HF Spaces terlalu lambat, akan lag/error
- ❌ Jangan upload video besar saat demo — proses lama di CPU
- ❌ Jangan refresh HF Spaces kalau sedang loading — tunggu saja

---

## Masalah yang Mungkin Muncul & Solusinya

| Masalah | Penyebab | Solusi Cepat |
|---------|----------|--------------|
| Login gagal | Railway crash / tabel belum sync | Cek Railway Logs, restart service |
| Data ayam tidak muncul | be2 tidur / Firebase belum konek | Buka URL HF Spaces dulu untuk wake up |
| "Firebase not connected" | Secret belum di-set di HF | Set `FIREBASE_SERVICE_ACCOUNT_BASE64` di HF Settings |
| Halaman loading lama | HF Spaces baru bangun dari tidur | Tunggu 30–60 detik, refresh |
| CORS error | `PUBLIC_BE2_URL` salah di Vercel | Pastikan URL pakai `-` bukan `/` |

---

## Keterbatasan yang Perlu Dijelaskan ke Penguji

1. **HF Spaces Free Tier (CPU)** — Inferensi YOLO lebih lambat dari GPU. Live counting real-time tidak optimal, tapi batch processing video tetap bisa berjalan.

2. **HF Spaces Sleep Mode** — Kalau tidak ada request selama ±15 menit, Space otomatis tidur. Request pertama setelah tidur butuh 30–60 detik untuk bangun.

3. **Upload file tidak permanen di HF** — File yang diupload (video, model baru) akan hilang kalau Space restart. Untuk produksi perlu external storage (Firebase Storage / S3).

4. **be3 (RFID Absensi) belum di-deploy** — Fitur absensi RFID belum terhubung ke dashboard.

---

## Kredensial

| Akun | Username/Email | Password |
|------|---------------|----------|
| Dashboard Admin | `admin@admin.com` | `Admin123!` |
| Firebase | akun Google kamu | — |
| Railway | akun Railway kamu | — |
| HF Spaces | akun HuggingFace kamu | — |
| Vercel | akun Vercel kamu | — |
