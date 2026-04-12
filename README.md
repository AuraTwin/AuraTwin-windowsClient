# AuraTwin Desktop Client

Official desktop application for **AuraTwin** — a privacy-first, AI-powered well-being assistant that builds your affective digital twin.

This is **Component 3** of the AuraTwin system: a lightweight Python app that runs silently in the background, captures webcam frames at configurable intervals, and transmits them securely to the AWS backend for emotion analysis.

> **Cross-platform:** Runs and builds on both **Windows** and **macOS**.

---

<p align="center">
  <img src="https://i.hizliresim.com/lo5si1v.png" width="45%" />
  &nbsp;&nbsp;
  <img src="https://i.hizliresim.com/mpgnia8.png" width="45%" />
</p>

---

## System Architecture 🏗️

| # | Component | Technology | Role |
|---|-----------|------------|------|
| 1 | **Backend & AI Engine** | AWS EC2 + FastAPI + EfficientNet + ONNX | Emotion analysis, Firestore writes |
| 2 | **Web Dashboard** | React + Firebase | User management, data visualization, App Key generation |
| **3** | **Desktop Client** *(this repo)* | **Python + PyQt5 + OpenCV** | Camera capture, secure transmission |
| 4 | **AI Reports** | Google Gemini 3.1 Flash Lite | Well-being reports and personalized recommendations |

### AI Model

AuraTwin utilizes the **enet_b0_8_best_afew** model — an EfficientNet-B0 variant optimized for emotion recognition. Deployed via **ONNX Runtime**, it achieves near-instant inference speeds on the AWS backend.

---

## How It Works 🔄

```
User signs in with App Key
        ↓
Client reads app_keys/{app_key} from Firestore   (READ only)
        ↓
Resolves uid → reads users/{uid}/profile/data    (READ only)
        ↓
Timer fires every N minutes (default: 5)
        ↓
Webcam opens → single frame captured → webcam closes immediately
        ↓
Frame encoded to Base64 in RAM (never written to disk)
        ↓
POST to AWS /predict-emotion  { app_key, image, timestamp }
        ↓
AWS: EfficientNet (ONNX) analyzes → writes to users/{uid}/emotions/{autoId}
        ↓
Image deleted from RAM on the server — no image ever persisted anywhere
```

> The client is **read-only** against Firestore. All emotion data writes belong exclusively to the AWS backend.

---

## Features ✨

- **🔑 Authentication** — App Key login (`ATV-XXXX-XXXX`) with direct Firestore validation and optional Remember Me
- **🔕 Background Operation** — Runs silently in System Tray / macOS Menu Bar; closing minimizes to tray
- **📷 Capture & Release** — Camera opens only for a single frame then is released immediately; skipped if camera is busy (Zoom, Teams, etc.)
- **⏸ Analysis Controls** — Pause/resume, configurable capture interval (1–60 min), color-coded status indicator
- **🌐 Bilingual UI** — Full Turkish and English support, switchable at any time, persisted in `config.json`

---

## Tech Stack 🛠️

| Library | Purpose |
|---------|---------|
| Python 3.x | Core application |
| PyQt5 | GUI, System Tray, dialogs |
| OpenCV (`cv2`) | Camera access and frame capture |
| Requests | HTTP POST to AWS `/predict-emotion` |
| python-dotenv | Loads Firebase credentials from `.env` |

---

## Download ⬇️

> **No Python required.** Just download and run.

| Platform | Download |
|----------|----------|
| Windows | [**AuraTwin.exe**](https://github.com/AuraTwin/AuraTwin-windowsClient/releases/) |
| macOS | [**AuraTwin.app**](https://github.com/AuraTwin/AuraTwin-windowsClient/releases/) |

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- A working webcam
- An AuraTwin account and App Key from [auratwin.netlify.app](https://auratwin.netlify.app)

### Steps

```bash
# 1. Clone
git clone https://github.com/AuraTwin/AuraTwin-desktopClient.git
cd AuraTwin-windowsClient

# 2. Configure environment
cp .env.example .env
# Fill in FIREBASE_PROJECT_ID, FIREBASE_API_KEY, AWS_API_URL

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

---

## Building from Source

Requires [PyInstaller](https://pyinstaller.org): `pip install pyinstaller`

```bash
# Windows → AuraTwin.exe
pyinstaller AuraTwin.spec

# macOS → AuraTwin.app
pyinstaller AuraTwin_macOS.spec
```

> **macOS:** `AuraTwin_macOS.spec` injects `NSCameraUsageDescription` into `Info.plist`. Do **not** use the Windows spec on macOS.

---

## Privacy & Security 🔒

- Frames are **never written to disk** — all encoding and transmission happen in RAM
- Camera is held open for milliseconds only (**Capture & Release** pattern)
- Firebase credentials live in `.env` and are never committed to source control
- The client only **reads** from Firestore — it never writes user data

---

## Project Information

**COMP4910 – Senior Design Project**
Yaşar University — Computer Engineering Department

| Name | Student ID |
|------|-----------|
| Ali Haktan SIĞIN | 21070001004 |
| Yiğit Emre ÇAY | 21070001008 |
| Utku DERİCİ | 21070001031 |
| Ahmet Özgür KORKMAZ | 21070001046 |

**Academic Advisor:** Doç. Dr. Mete Eminağaoğlu

**Related:** [Web Dashboard](https://auratwin.netlify.app) · [GitHub Organization](https://github.com/AuraTwin)

---

© 2026 AuraTwin Project Team
