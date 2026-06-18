# Setup di Device Baru — AI-FRSS Dashboard

## Prasyarat

Install semua ini sebelum mulai:

| Software | Versi Minimum | Link Download |
|----------|--------------|---------------|
| Node.js | v18+ | https://nodejs.org |
| Python | 3.10+ | https://python.org |
| Git | terbaru | https://git-scm.com |

Cek apakah sudah terinstall:
```bash
node --version    # harus v18+
python3 --version # harus 3.10+
git --version
```

---

## Langkah 1 — Clone Repository

```bash
git clone https://github.com/D4ce394/Chicken-Poultry.git
cd Chicken-Poultry
```

---

## Langkah 2 — Setup File Konfigurasi

> File `.env` tidak ikut di-clone (sengaja diabaikan). Buat secara manual.

### be/.env
```bash
# Buat file be/.env
cat > be/.env << 'EOF'
PORT=3000
NODE_ENV=development
BASE_URL=http://localhost:3000
JWT_ACCESS_TOKEN_SECRET=a5d269d970eb746565c3b9d44cb9f4cec128b547b026e30628889e1905e1b71a729632839cacc9e6b8ce4d07f2d7546bb0cd83235901fbfd3c1a20345dfb7ec6
EOF
```

### be2/.env
```bash
# Buat file be2/.env
cat > be2/.env << 'EOF'
PORT=8000
FIREBASE_DATABASE_URL=https://rfid-de0fd-default-rtdb.asia-southeast1.firebasedatabase.app
FIREBASE_SERVICE_ACCOUNT_PATH=./rfid-de0fd-firebase-adminsdk-fbsvc-22ca2974df.json
SECRET_KEY=6687b06e53c0de1331d640e729ff90524ff712c7bb17f882c0ce316d7d68ec2d
INFERENCE_DEVICE=cpu
LOG_LEVEL=INFO
EOF
```

### fe/.env
```bash
# Buat file fe/.env
cat > fe/.env << 'EOF'
PUBLIC_API_URL=http://localhost:3000/api
PUBLIC_BE2_URL=http://localhost:8000
EOF
```

---

## Langkah 3 — Salin Firebase Credential

File credential Firebase **tidak ikut di-clone** karena alasan keamanan. Salin file berikut dari device asal ke folder `be2/`:

```
be2/rfid-de0fd-firebase-adminsdk-fbsvc-22ca2974df.json
```

> Minta file ini dari pemilik project atau download ulang dari:  
> Firebase Console → Project Settings → Service Accounts → Generate new private key

---

## Langkah 4 — Install Dependencies

### 4a. Frontend (fe)
```bash
cd fe
npm install
cd ..
```

### 4b. Backend 1 (be)
```bash
cd be
npm install
cd ..
```

### 4c. Backend 2 (be2) — Python
```bash
cd be2
python3 -m venv venv

# Linux / Mac:
source venv/bin/activate

# Windows:
# venv\Scripts\activate

pip install -r requirements.txt
cd ..
```

> ⚠️ Proses ini bisa memakan waktu 5–15 menit karena mengunduh PyTorch dan Ultralytics YOLO.

---

## Langkah 5 — Jalankan Semua Service

### Cara Cepat (otomatis buka 3 terminal)
```bash
./start-local.sh
```

### Cara Manual (3 terminal terpisah)

**Terminal 1 — BE1:**
```bash
cd be
npm run build
node dist/server.js
```

**Terminal 2 — BE2:**
```bash
cd be2
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3 — Frontend:**
```bash
cd fe
npm run dev
```

---

## Langkah 6 — Buka Dashboard

Setelah semua terminal menunjukkan "running / ready":

Buka browser → **http://localhost:5173**

Login dengan:
- Email: `admin@admin.com`
- Password: `Admin123!`

---

## Ringkasan Port

| Service | URL |
|---------|-----|
| Dashboard (fe) | http://localhost:5173 |
| API Backend 1 (be) | http://localhost:3000/api |
| API Backend 2 (be2) | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## Troubleshooting

**`npm: command not found`**  
→ Install Node.js dari https://nodejs.org

**`python3: command not found`**  
→ Install Python dari https://python.org  
→ Di Windows pastikan centang "Add to PATH" saat install

**`SQLITE_ERROR: no such table`**  
→ Tabel akan dibuat otomatis saat be pertama kali dijalankan. Tunggu beberapa detik.

**`Firebase not connected`**  
→ Pastikan file `be2/rfid-de0fd-firebase-adminsdk-fbsvc-22ca2974df.json` sudah ada  
→ Cek path di `be2/.env` → `FIREBASE_SERVICE_ACCOUNT_PATH`

**`ModuleNotFoundError`** (be2)  
→ Pastikan virtual environment sudah aktif (`source venv/bin/activate`)  
→ Jalankan ulang `pip install -r requirements.txt`

**Port already in use**  
```bash
# Cari dan matikan proses yang memakai port
lsof -i :3000    # ganti port sesuai yang error
kill -9 <PID>
```
