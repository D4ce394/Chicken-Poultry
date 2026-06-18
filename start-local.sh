#!/bin/bash
# ─── Jalankan semua service di terminal terpisah ───────────────────────────
ROOT="$(cd "$(dirname "$0")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Membuka terminal untuk setiap service...${NC}"

# ─── Backend 1 (be - Express + SQLite, port 3000) ──────────────────────────
gnome-terminal \
  --title="BE1 — Express API (port 3000)" \
  -- bash -c "
    cd '$ROOT/be'
    echo -e '\033[0;32m[BE1] Building...\033[0m'
    npm run build
    echo -e '\033[0;32m[BE1] Starting Express server...\033[0m'
    node dist/server.js
    echo -e '\033[0;31mBE1 berhenti. Tekan Enter untuk tutup.\033[0m'
    read
  " &

sleep 1

# ─── Backend 2 (be2 - FastAPI + YOLO, port 8000) ──────────────────────────
gnome-terminal \
  --title="BE2 — FastAPI + YOLO (port 8000)" \
  -- bash -c "
    cd '$ROOT/be2'
    if [ ! -d venv ]; then
      echo -e '\033[1;33m[BE2] Membuat venv...\033[0m'
      python3 -m venv venv
      ./venv/bin/pip install -r requirements.txt
    fi
    echo -e '\033[0;32m[BE2] Starting FastAPI server...\033[0m'
    ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    echo -e '\033[0;31mBE2 berhenti. Tekan Enter untuk tutup.\033[0m'
    read
  " &

sleep 1

# ─── Frontend (SvelteKit dev, port 5173) ───────────────────────────────────
gnome-terminal \
  --title="FE — SvelteKit Dashboard (port 5173)" \
  -- bash -c "
    cd '$ROOT/fe'
    echo -e '\033[0;32m[FE] Starting SvelteKit dev server...\033[0m'
    npm run dev
    echo -e '\033[0;31mFE berhenti. Tekan Enter untuk tutup.\033[0m'
    read
  " &

sleep 2

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  3 terminal terbuka!                      ${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "  Dashboard : ${YELLOW}http://localhost:5173${NC}"
echo -e "  API be1   : ${YELLOW}http://localhost:3000/api${NC}"
echo -e "  API be2   : ${YELLOW}http://localhost:8000${NC}"
echo ""
echo -e "  Login: ${YELLOW}admin@admin.com${NC} / ${YELLOW}Admin123!${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
