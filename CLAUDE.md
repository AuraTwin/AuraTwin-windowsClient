# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AuraTwin Windows Client is a single-file Python desktop app (`main.py`) that captures webcam frames at configurable intervals and POSTs them to an AWS backend for emotion analysis. It is **Component 3** of the larger AuraTwin system.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app (requires .env to be configured)
python main.py

# Build a standalone Windows .exe (requires PyInstaller)
pyinstaller AuraTwin.spec
```

## Environment Setup

Copy `.env.example` to `.env` and fill in:
```
FIREBASE_PROJECT_ID=...
FIREBASE_API_KEY=...
AWS_API_URL=http://your-aws-endpoint/predict-emotion
```

The app reads `.env` at startup via `python-dotenv`. In the frozen `.exe`, `.env` is bundled into the PyInstaller archive (see `AuraTwin.spec`).

## Architecture

Everything lives in `main.py`. The key classes and their roles:

| Class / Function | Role |
|---|---|
| `firestore_get` / `validate_app_key` | REST calls to Firestore v1 API (no Firebase SDK — raw HTTP with API key) |
| `LoginWindow(QWidget)` | First screen: App Key entry, Remember Me, language selector |
| `MainWindow(QWidget)` | Post-login screen: status indicator, settings button, tray integration |
| `SettingsDialog(QDialog)` | Pause/resume, interval picker (dropdown), language switch |
| `TestDialog(QDialog)` | Live camera preview + manual capture-and-send for demos |

**Auth flow:** App Key → Firestore `app_keys/{key}` → resolve `uid` → Firestore `users/{uid}/profile/data` → get name/surname. The client is **read-only** against Firestore; all emotion writes happen on the AWS side.

**Capture loop:** `QTimer` fires every N minutes → `cv2.VideoCapture(0)` opens, reads one frame, closes immediately → frame encoded to Base64 in RAM → `requests.post` to `AWS_API_URL`. If the camera is busy (non-zero OpenCV error), the cycle is skipped silently.

**Bilingual UI:** All user-visible strings live in the `STRINGS` dict at the top of `main.py` with `"tr"` and `"en"` keys. Call `self.t("key")` (defined on `MainWindow`) to get the current language string. Language and credentials are persisted to `config.json` in the working directory.

**PyInstaller bundle:** `AuraTwin.spec` produces a single-file `console=False` exe. `.env` and `AuraTwin_Logo.png` are included as `datas`. At runtime, the frozen app resolves paths via `sys._MEIPASS`; the `BASE_DIR` variable at the top of `main.py` handles both frozen and unfrozen cases.
