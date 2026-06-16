# 🎥 AI-Powered Face Recognition Surveillance System - Dashboard

A high-performance web-based surveillance dashboard to monitor, analyze, and manage thousands of CCTV cameras with AI insights. Includes facial recognition, real-time alerts, live streams, and analytics.

---

## 🚀 Tech Stack

| Component          | Technology                  | Reason                                     |
|-------------------|-----------------------------|--------------------------------------------|
| Frontend          | SvelteKit + TailwindCSS     | Fast, lightweight, real-time performance   |
| Backend           | FastAPI (Python)            | High-performance API server                |
| Database          | PostgreSQL + pgvector       | Efficient storage for embeddings & logs    |
| Streaming         | WebRTC (Mediasoup)          | Real-time video with low latency           |
| WebSockets        | FastAPI + Redis Pub/Sub     | Live AI alert delivery                     |
| Search Engine     | Elasticsearch               | Fast indexed search                        |
| Auth              | OAuth2 / JWT                | Secure multi-user system                   |

---

## 📋 Features Overview

### 🔐 Authentication
- Login (Username, Password, 2FA)
- Forgot Password

### 🏠 Dashboard
- System Summary
- Active Cameras & Alerts
- Statistics & Full-Screen Camera View

### 📢 AI Alerts & Notifications
- Motion, Intrusion, Face Match, Blacklist Alerts
- Notification Center with Sound & Popups

### 🎭 Face Recognition & Attendance
- Face Log with Confidence Scores
- Attendance Report
- Blacklist Detection

### 🎞️ Video Archive
- Playback with Timeline & Events
- Image Snapshots
- Filtering by Person, Date, Camera

### 📊 Reports & Analytics
- Incident Reports
- Heatmaps (Crowd, Motion)
- Export to CSV, PDF, Excel

### 📷 Camera & System Management
- RTSP Health Monitor
- AI Sensitivity & Storage Settings
- Notification Preferences

### 👥 User & Role Management
- Admin / Operator Roles
- Blacklist Management
- Access Permissions (RBAC)

---

## 📐 UI/UX Highlights

- 🔲 Dynamic Grid View (1, 4, 9, 16 cameras)
- 🎯 AI Overlay with detection box & confidence
- 🔔 Live Alerts Timeline
- 🔍 Face Search from images or logs
- 📊 System Health Monitor (GPU, Stream, Storage)

---

## 🧩 How to Run the Project

### 🗄️ Backend (Database Setup)
1. Jalankan XAMPP / MySQL
2. Buat database bernama: `sv-fs.sqlite`
3. Import file `sv-fs.sqlite.sql` ke database tersebut  
   _(pastikan file `sv-fs.sqlite.sql` ada di folder proyek)_

---

### 🖥️ Backend App (API & Server)
1. Masuk ke folder backend
2. Jalankan:
```bash
npm install
npm run dev
```

---

### 💻 Frontend App (Svelte Dashboard)
> Gunakan **Yarn**, karena `npm` bisa error di beberapa mesin

1. Install Yarn jika belum:
```bash
npm install --global yarn
```

2. Jalankan frontend:
```bash
yarn install
yarn dev
```

3. Akses di browser:
```
http://localhost:5173
```


## 📡 Scalability & Deployment

| Aspect                 | Solution                            |
|------------------------|-------------------------------------|
| Web App Deployment     | Docker + Kubernetes                 |
| Load Balancing         | Nginx + Cloudflare                  |
| Real-Time Processing   | WebSockets + Kafka                  |
| DB Scaling             | PostgreSQL + Redis                  |

---

## 🧠 Best Practices

- Use **WebRTC** for real-time streaming
- Store AI logs in **PostgreSQL + pgvector**
- Real-time updates via **WebSockets**
- Monitor system health (GPU, Storage, Network)
- Secure access with **OAuth2/JWT** and RBAC

---


## 📄 License

This project is intended for academic and research purposes only.  
Commercial use is not permitted without permission.

