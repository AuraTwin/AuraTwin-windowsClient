# AuraTwin Desktop Client

Official desktop application for **AuraTwin** — a privacy-first, AI-powered well-being assistant that builds your affective digital twin.

This repository is **Component 3** of the AuraTwin system: a lightweight Python application that runs silently in the background, captures webcam frames at configurable intervals, and transmits them securely to the AWS backend for emotion analysis.

> **Cross-platform:** Runs and builds on both **Windows** and **macOS**.

---

## System Architecture

AuraTwin is built on four tightly integrated components:

| # | Component | Technology | Role |
|---|-----------|------------|------|
| 1 | **Backend & AI Engine** | AWS EC2 + FastAPI + Mini-Xception | Emotion analysis, Firestore writes |
| 2 | **Web Dashboard** | React/Vue + Firebase | User management, data visualization, App Key generation |
| **3** | **Desktop Client** *(this repo)* | **Python + PyQt5 + OpenCV** | Camera capture, secure transmission |
| 4 | **Digital Twin / AI Reports** | Google Gemini 2.5 Flash | Weekly well-being reports and personalized recommendations |

---

## How It Works

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
AWS: Mini-Xception analyzes → writes to users/{uid}/emotions/{autoId}
        ↓
Image deleted from RAM on the server — no image ever persisted anywhere
```

> The client is **read-only** against Firestore. All emotion data writes belong exclusively to the AWS backend.

---

## Features

### Authentication
- App Key login in `ATV-XXXX-XXXX` format
- Direct Firestore validation — no intermediate backend needed at login
- **Remember Me** — saves credentials locally in `config.json` for automatic re-login on startup
- Graceful error handling for connection errors, permission errors, and invalid keys

### Background Operation
- Runs silently in the **System Tray** or **macOS Menu Bar**
- Right-click tray menu: Show, Go to Dashboard, Quit
- Closing the window minimizes to tray — the app never stops unexpectedly

### Capture & Release Camera
- Camera is opened **only for the single frame capture** then immediately released
- If the camera is busy (Zoom, Teams, Meet, etc.) the capture cycle is skipped — no conflicts
- Frames are **never saved to disk** at any point; all encoding happens in RAM

### Analysis Controls
- **Pause / Resume** analysis from the Settings dialog
- Configurable capture interval: **1–60 minutes** (recommended: 5 min)
- Color-coded live status indicator:
  - `● Active — Analysis running` (green)
  - `⏸ Analysis paused` (amber)
  - `● Camera not found / busy` (red)
  - `Connection error` / `Invalid App Key` (red)

### Bilingual UI
- Full **Turkish and English** support across all screens and dialogs
- Language can be switched at any time from the login screen or Settings dialog
- Language preference is persisted in `config.json`

---

## Firestore Data Structure

```
app_keys/{app_key}
  Fields : uid (string), created_at (Timestamp)
  Access : Client READS (login only), Web WRITES

users/{uid}/profile/data
  Fields : name, surname, email, app_key, created_at
  Access : Client READS (login only), Web READS & WRITES

users/{uid}/emotions/{autoId}
  Fields : timestamp, emotion_label, confidence
  Access : AWS WRITES only — Client never touches this

users/{uid}/last_report/data
  Fields : generated_at, content
  Access : Web READS & WRITES (Gemini reports)
```

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| Python 3.x | Core application |
| PyQt5 | GUI windows, System Tray, Settings dialog |
| OpenCV (`cv2`) | Camera access and frame capture |
| Requests | HTTP POST to AWS `/predict-emotion` |
| python-dotenv | Loads Firebase credentials from `.env` |
| Base64 / JSON | In-memory image encoding, local config |

---

## Download

> **No Python required.** Just download and run.

| Platform | Download |
|----------|----------|
| Windows | [**AuraTwin.exe**](https://github.com/AuraTwin/AuraTwin-windowsClient/releases/) |
| macOS | [**AuraTwin.app**](https://github.com/AuraTwin/AuraTwin-windowsClient/releases/) |

Or visit the [Releases page](https://github.com/AuraTwin/AuraTwin-windowsClient/releases) for all versions.

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- A working webcam
- An AuraTwin account and App Key from [auratwin.netlify.app](https://auratwin.netlify.app)

### 1. Clone the repository

```bash
git clone https://github.com/AuraTwin/AuraTwin_Client.git
cd AuraTwin_Client
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_API_KEY=your-firebase-api-key
AWS_API_URL=http://your-aws-endpoint/predict-emotion
```

### 3. Install dependencies

```bash
# Cross-platform (recommended)
pip3 install -r requirements_client.txt
```

### 4. Run the application

```bash
# macOS / Linux
python3 main.py

# Windows
python main.py
```

---

## Building from Source

Requires [PyInstaller](https://pyinstaller.org): `pip3 install pyinstaller`

### Windows → AuraTwin.exe

```bash
pyinstaller AuraTwin.spec
# Output: dist/AuraTwin.exe
```

### macOS → AuraTwin.app

```bash
pyinstaller AuraTwin_macOS.spec
# Output: dist/AuraTwin.app
```

> **macOS camera access:** The `AuraTwin_macOS.spec` file injects `NSCameraUsageDescription` into the app bundle's `Info.plist`. Without this, macOS will silently deny camera access. Do **not** use the Windows spec to build on macOS.

---

## First-Time Setup

1. Launch the app — the login screen appears.
2. Enter your **App Key** (`ATV-XXXX-XXXX`) from the AuraTwin Dashboard.
3. (Optional) Check **Remember Me** to skip login on future launches.
4. Click **Sign In**.
5. The app switches to the status screen and begins background analysis immediately.

To adjust settings, click **⚙ Settings** to:
- Change the capture interval (1–60 minutes)
- Pause or resume analysis
- Switch the UI language (TR / EN)

---

## Application Screenshots

<p align="center">
  <img src="https://i.hizliresim.com/lo5si1v.png" width="45%" />
  &nbsp;&nbsp;
  <img src="https://i.hizliresim.com/mpgnia8.png" width="45%" />
</p>

---

## Privacy & Security

- Captured frames are **never written to disk** — encoding and transmission happen entirely in RAM
- The camera is held open for milliseconds only (**Capture & Release** pattern)
- Firebase credentials are stored in `.env` and **never committed to source control**
- The client only **reads** from Firestore at login — it never writes user data
- All emotion data writes are performed exclusively by the AWS backend using Firebase Admin SDK

---

## Project Information

**COMP4910 – Senior Design Project**
Yaşar University — Computer Engineering Department

### Team

| Name | Student ID |
|------|-----------|
| Ali Haktan SIĞIN | 21070001004 |
| Yiğit Emre ÇAY | 21070001008 |
| Utku DERİCİ | 21070001031 |
| Ahmet Özgür KORKMAZ | 21070001046 |

**Academic Advisor:** Doç. Dr. Mete Eminağaoğlu

---

## Related Repositories

- **Web Dashboard:** [auratwin.netlify.app](https://auratwin.netlify.app)
- **GitHub Organization:** [github.com/AuraTwin](https://github.com/AuraTwin)

---

© 2026 AuraTwin Project Team
