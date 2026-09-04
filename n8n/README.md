# MarketVoice SEA — n8n Dedicated Workspace & Workflow Automation

**Path**: `C:\Users\Arilano\Downloads\Project ARICE\Project SEA\n8n`  
**Modul**: Operational Decision Support System (DSS) Review Triage & Orchestration  
**Status**: `SYNTHETIC_OPERATIONAL_DEMONSTRATION`  
**Port**: `5678` (Web UI & Webhook Intake)  
**Database Integrasi**: PostgreSQL `localhost:5432` (`marketvoice_dev` -> `marketvoice_warehouse`)  
**Microservice Integrasi**: FastAPI `http://localhost:8000` (`/v1/review/analyze`, `/v1/decision/evaluate`)  

---

## 1. Struktur Workspace Khusus n8n

Folder ini adalah workspace mandiri (*self-contained dedicated workspace*) khusus untuk seluruh operasi n8n:

```text
n8n/
├── n8n.code-workspace                     # VS Code / Antigravity Dedicated Workspace file
├── README.md                              # Dokumentasi teknis & panduan operasional
├── package.json                           # Manifest Node.js & lifecycle npm scripts
├── .env.example                           # Template variabel lingkungan
├── .env                                   # Konfigurasi aktif (Postgres, FastAPI host, port)
├── docker-compose.yml                     # Opsi deployment containerized dengan volume persisten
├── workflows/                             # Definisi workflow JSON versi terkontrol
│   └── marketvoice_review_triage.json     # 12-node DAG review triage & routing
├── fixtures/                              # Event synthetic review payloads (P1–P4) mandiri
│   ├── synthetic_p1_event.json            # P1 Chronic defect event
│   ├── synthetic_p2_event.json            # P2 Order inaccuracy event
│   ├── synthetic_p3_event.json            # P3 Packaging issue event
│   ├── synthetic_p4_event.json            # P4 Informational review with PII
│   └── sample_review_events.json          # Dataset gabungan fixtures
├── scripts/                               # Skrip otomasi, launcher & validasi
│   ├── start_n8n.bat                      # Windows 1-Click Batch Launcher (Double-click ready)
│   ├── start_n8n.ps1                      # Windows PowerShell automated launcher
│   ├── start_n8n.sh                       # Unix/Mac/WSL launcher
│   ├── check_system_health.py             # Pemeriksa kesehatan sistem & zero-error audit
│   ├── trigger_webhook_test.py            # Test harness pengujian integrasi webhook
│   └── validate_workflow_syntax.py        # Static schema & node graph validator
└── data/                                  # Direktori persisten SQLite n8n lokal (.gitignored)
    ├── database.sqlite                    # Database internal n8n (workflows & executions)
    └── config                             # Pengaturan runtime n8n
```

---

## 2. Pemeriksaan Kesehatan Sistem (*System Error Pre-Flight Check*)

Untuk memastikan tidak ada kesalahan konfigurasi (*system error*), jalankan skrip audit kesehatan:

```powershell
python n8n\scripts\check_system_health.py
```

Skrip ini secara otomatis memverifikasi:
1. **Node.js & npm runtime**: Deteksi versi dan kesiapan eksekusi.
2. **Integritas File**: Memastikan seluruh 15 file utama di folder `n8n/` lengkap.
3. **Validasi DAG Workflow**: Schema JSON 12 node valid tanpa dangling edges.
4. **Persistensi SQLite**: Integritas tabel database n8n lokal.
5. **Koneksi PostgreSQL**: Ketersediaan database `marketvoice_dev` dan tabel operasional (`operational_event_log`, `human_review_case`).
6. **Port Probe & Microservice**: Ketersediaan port 5678 (n8n) dan status FastAPI (port 8000).

---

## 3. Cara Menjalankan n8n (*Quickstart*)

Pilih salah satu cara di bawah ini:

### Opsi A: 1-Click Launcher (Windows Batch - Paling Mudah)
Cukup double-click file:
```text
n8n\scripts\start_n8n.bat
```
Atau jalankan dari terminal:
```cmd
.\n8n\scripts\start_n8n.bat
```

### Opsi B: Via PowerShell Launcher
```powershell
powershell -ExecutionPolicy Bypass -File .\n8n\scripts\start_n8n.ps1
```

### Opsi C: Via npm Scripts
```powershell
cd n8n
npm run start:local
```

### Opsi D: Via Docker Compose
```bash
cd n8n
docker compose up -d
```

Setelah server n8n aktif, buka browser Anda di:  
👉 **http://localhost:5678**

---

## 4. Validasi Sintaks Workflow & Pengujian Otomatis

### A. Validasi Sintaks & Topologi Node:
```powershell
python n8n\scripts\validate_workflow_syntax.py
```

### B. Menjalankan Simulasi Webhook (P1 - P4):
*Pastikan FastAPI sudah berjalan (`python scripts/runners/start_api.py`) dan n8n aktif di port 5678*:
```powershell
python n8n\scripts\trigger_webhook_test.py
```

---

## 5. Keamanan & Kebijakan Data (.gitignore)
- `n8n/data/` (termasuk SQLite database dan credentials) sepenuhnya masuk dalam `.gitignore`.
- Tidak ada password atau kunci rahasia yang di-commit ke repositori git publik.
