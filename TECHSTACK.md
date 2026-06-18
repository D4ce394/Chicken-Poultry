# Tech Stack — AI-FRSS Dashboard

## Gambaran Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│                     PENGGUNA (Browser)                  │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   Frontend (fe)     │
              │   SvelteKit · Vercel│
              └──────┬──────┬───────┘
                     │      │
          ┌──────────▼─┐  ┌─▼────────────────┐
          │  Backend 1  │  │   Backend 2       │
          │  Express    │  │   FastAPI + YOLO  │
          │  Railway    │  │   HF Spaces       │
          └──────┬──────┘  └──────┬────────────┘
                 │                │
          ┌──────▼──────┐  ┌──────▼──────────┐
          │   SQLite    │  │    Firebase      │
          │  (Railway   │  │  Realtime DB     │
          │   Volume)   │  │  (Google Cloud)  │
          └─────────────┘  └─────────────────┘
```

---

## Frontend (fe)

| Kategori | Teknologi | Versi |
|----------|-----------|-------|
| Framework | SvelteKit | ^2.16.0 |
| UI Library | Svelte | ^5.0.0 |
| Bahasa | TypeScript | ^5.0.0 |
| Styling | Tailwind CSS | ^4.0.0 |
| Build Tool | Vite | ^6.2.6 |
| HTTP Client | Axios | ^1.9.0 |
| Charts | ApexCharts + svelte-chart-apex | ^3.45.0 |
| Icons | Lucide Svelte | ^0.511.0 |
| Form Validation | Felte + Zod | ^1.3.0 / ^3.24.4 |
| Server Adapter | adapter-auto (Vercel) / adapter-node (lokal) | — |
| Deployment | Vercel | — |

---

## Backend 1 — API Utama (be)

| Kategori | Teknologi | Versi |
|----------|-----------|-------|
| Runtime | Node.js | v18.19.1 |
| Framework | Express | ^4.21.1 |
| Bahasa | TypeScript | ^5.7.3 |
| ORM | Sequelize | ^6.37.4 |
| Database | SQLite3 | ^5.1.7 |
| Autentikasi | JWT (jsonwebtoken) | ^9.0.2 |
| Enkripsi Password | bcrypt | ^5.1.1 |
| Validasi | Joi | ^17.13.3 |
| Logging | Winston + daily-rotate | ^3.15.0 |
| API Docs | Swagger (OpenAPI) | ^6.2.8 |
| Deployment | Railway | — |
| Storage | SQLite pada persistent volume `/data` | — |

---

## Backend 2 — AI & Firebase (be2)

| Kategori | Teknologi | Versi |
|----------|-----------|-------|
| Runtime | Python | 3.12.3 |
| Framework | FastAPI | 0.111.0 |
| ASGI Server | Uvicorn | 0.29.0 |
| Validasi | Pydantic | 2.8.0 |
| Computer Vision | OpenCV (headless) | 4.8.1.78 |
| Object Detection | Ultralytics YOLO | 8.3.168 |
| Deep Learning | PyTorch | 2.3.0 |
| Image Processing | Pillow | 10.3.0 |
| Database (async) | SQLAlchemy 2.0 + aiosqlite | 2.0.36 / 0.20.0 |
| Firebase | firebase-admin | 6.5.0 |
| Autentikasi | PyJWT + bcrypt | — |
| Data Analysis | Pandas, NumPy, Matplotlib | — |
| Deployment | Hugging Face Spaces (CPU Basic) | — |

---

## Backend 3 — RFID & Absensi (be3)

| Kategori | Teknologi | Versi |
|----------|-----------|-------|
| Runtime | Node.js | — |
| Framework | Express | ^5.1.0 |
| Database | MySQL | 8.0 |
| Autentikasi | JWT | ^9.0.2 |
| Password | bcrypt | ^6.0.0 |
| Media Storage | Cloudinary | — |
| Real-time | WebSocket (ws) | ^8.18.2 |

---

## Database & Storage

| Komponen | Teknologi | Lokasi |
|----------|-----------|--------|
| Data pengguna, kamera, recording | SQLite | Railway persistent volume |
| Data hitungan ayam (real-time) | Firebase Realtime Database | Google Cloud (asia-southeast1) |
| Model YOLO (.pt files) | Filesystem | Dalam Docker image be2 |
| Upload video/gambar | Filesystem | Docker volume `be2_uploads` |
| Data RFID & absensi | MySQL | Docker volume (lokal) |
| Foto/media wajah | Cloudinary CDN | Cloud |

---

## Infrastructure & DevOps

| Komponen | Teknologi |
|----------|-----------|
| Containerisasi | Docker (multi-stage build) |
| Orkestrasi lokal | Docker Compose |
| Frontend hosting | Vercel |
| Backend 1 hosting | Railway |
| Backend 2 hosting | Hugging Face Spaces |
| Firebase | Google Firebase (Realtime DB) |
| Source control | Git + GitHub |
| File besar (model .pt) | Git LFS |

---

## Fitur Utama Sistem

| Fitur | Teknologi Kunci |
|-------|----------------|
| Autentikasi & otorisasi | JWT, bcrypt, role-based |
| Live camera monitoring | WebSocket, HLS stream |
| Chicken counting otomatis | YOLO v8, PyTorch, OpenCV |
| Rekap & laporan | Firebase Realtime DB, ApexCharts |
| Upload & proses video | FastAPI multipart, YOLO batch |
| RFID absensi | WebSocket, MySQL |
| Face recognition | OpenCV, Cloudinary |
| API dokumentasi | Swagger / OpenAPI |
