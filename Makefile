.PHONY: help setup dev docker docker-build docker-down logs \
        be be2 be3 fe fe-build fe-firebase

# ──────────────────────────────────────────────
#  Tampilkan semua perintah
# ──────────────────────────────────────────────
help:
	@echo ""
	@echo "  AI-FRSS Dashboard — Perintah Tersedia"
	@echo "  ───────────────────────────────────────────────────"
	@echo "  DOCKER (cara paling gampang):"
	@echo "    make docker        — build + jalankan semua service"
	@echo "    make docker-build  — build ulang image lalu jalankan"
	@echo "    make docker-down   — stop semua container"
	@echo "    make logs          — lihat log semua service (Ctrl+C untuk keluar)"
	@echo ""
	@echo "  LOKAL (tanpa Docker, satu-satu):"
	@echo "    make setup         — install dependencies semua backend"
	@echo "    make be            — jalankan be  (Express + Prisma, port 3000)"
	@echo "    make be2           — jalankan be2 (FastAPI + YOLO, port 8000)"
	@echo "    make be3           — jalankan be3 (Express face-rec, port 3002)"
	@echo "    make fe            — jalankan fe  (SvelteKit dev, port 5173)"
	@echo ""
	@echo "  FIREBASE:"
	@echo "    make fe-firebase   — build static untuk Firebase Hosting"
	@echo "    make firebase-deploy — build + deploy ke Firebase"
	@echo "  ───────────────────────────────────────────────────"
	@echo ""

# ──────────────────────────────────────────────
#  DOCKER
# ──────────────────────────────────────────────
docker:
	@if [ ! -f .env ]; then cp .env.example .env; echo "⚠  .env dibuat dari .env.example — silakan isi secrets di .env"; fi
	docker compose up

docker-build:
	@if [ ! -f .env ]; then cp .env.example .env; echo "⚠  .env dibuat dari .env.example — silakan isi secrets di .env"; fi
	docker compose up --build

docker-down:
	docker compose down

logs:
	docker compose logs -f

# ──────────────────────────────────────────────
#  INSTALL DEPENDENCIES (lokal)
# ──────────────────────────────────────────────
setup:
	@echo "→ Install be..."
	cd be && npm install
	@echo "→ Install fe..."
	cd fe && npm install
	@echo "→ Install be3..."
	cd be3 && npm install
	@echo "→ Setup be2 (Python venv)..."
	cd be2 && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
	@echo "✓ Semua dependency terinstall"

# ──────────────────────────────────────────────
#  JALANKAN LOKAL (masing-masing backend)
# ──────────────────────────────────────────────
be:
	@if [ ! -f be/.env ]; then cp be/.env.example be/.env; echo "⚠  be/.env dibuat — isi dulu sebelum lanjut"; fi
	cd be && npm run dev

be2:
	@if [ ! -f be2/.env ]; then cp be2/.env.example be2/.env; echo "⚠  be2/.env dibuat — isi dulu sebelum lanjut"; fi
	@if [ ! -d be2/venv ]; then echo "→ Setup venv..."; cd be2 && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt; fi
	cd be2 && ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

be3:
	@if [ ! -f be3/.env ]; then cp be3/.env.example be3/.env; echo "⚠  be3/.env dibuat — isi dulu sebelum lanjut"; fi
	cd be3 && npm start

fe:
	@if [ ! -f fe/.env ]; then cp fe/.env.example fe/.env; echo "⚠  fe/.env dibuat — isi PUBLIC_API_URL jika perlu"; fi
	cd fe && npm run dev

# ──────────────────────────────────────────────
#  FIREBASE
# ──────────────────────────────────────────────
fe-firebase:
	@if [ ! -f fe/.env ]; then echo "ERROR: buat fe/.env dulu dan isi PUBLIC_API_URL dengan URL backend production"; exit 1; fi
	cd fe && npm run build:firebase
	@echo "✓ Build selesai di fe/build/ — siap deploy"

firebase-deploy: fe-firebase
	npx firebase deploy --only hosting
