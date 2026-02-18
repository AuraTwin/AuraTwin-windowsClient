# AuraTwin Windows Client 💻

Official desktop application for AuraTwin — An Affective Digital Twin for Personalized Well-being and Self-Correction.

This repository contains the **Windows “sensor” component** of the AuraTwin system: a lightweight Python application that runs in the background to capture and process emotional data securely.

---

## 📖 About

This is the Windows Client repository for our graduation project at **Yaşar University – Computer Engineering Department**.

AuraTwin aims to create an affective digital twin that supports personalized well-being and self-correction. The Windows client acts as the sensing layer of the system.

The application is designed to monitor user well-being without intruding on daily tasks. It utilizes **“Capture & Release” technology** to ensure privacy while providing high-frequency emotional data for the digital twin.

All captured data is processed temporarily in memory and securely transmitted to the backend infrastructure.

---

## 🏗️ System Role

The Windows Client serves as:

- 📷 Emotional data capture layer  
- 🧠 Local preprocessing unit  
- 🔐 Secure transmission agent  
- 🔄 Continuous background sensor  

It is intentionally lightweight and optimized for minimal system impact.

---

## 🚀 Tech Stack

- **Python** – Core application logic  
- **OpenCV (cv2)** – Camera access and image processing  
- **PyQt5** – Modern GUI and System Tray integration  
- **Requests** – Secure communication with AWS backend  
- **Base64** – In-memory image encoding (privacy-first architecture)  

---

## ✨ Key Features

### 🔒 Privacy-First Architecture
- Images are **never saved to disk**  
- All processing happens in RAM  
- No local image storage  
- Direct secure transmission  

### ☁️ Edge Processing
- Frames are encoded into Base64 format  
- Prepared for secure API communication  
- Lightweight transmission payload  

### 🤫 Background Mode
- Runs silently in the **System Tray**  
- Does not interrupt workflow  
- Minimal CPU and memory usage  

### ⚡ Smart Collision Detection
- Detects camera usage conflicts  
- Skips capture cycles if another app (Zoom, Meet, etc.) is using the camera  
- Prevents system instability  

### 🔑 Token-Based Authentication
- Each client is linked using a unique App Key  
- Secure pairing with the AuraTwin web dashboard  
- Authenticated API communication  

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/KULLANICI_ADIN/AuraTwin-windowsClient.git
cd AuraTwin-windowsClient
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application

```bash
python main.py
```

---

## ⚙️ Configuration

1. Log in to your **AuraTwin Dashboard**.
2. Retrieve your **App Key**.
3. Open the Windows Client settings.
4. Enter the App Key to link your device.

After successful authentication, the client will begin secure background operation.

---

## 🔐 Privacy & Security Principles

- No image persistence  
- In-memory processing only  
- Secure HTTPS communication  
- Token-based authentication  
- Minimal data retention philosophy  

AuraTwin prioritizes user privacy while maintaining high-frequency emotional state tracking.

---

## 👥 Team

- **Ali Haktan SIĞIN** – 21070001004  
- **Yiğit Emre ÇAY** – 21070001008  
- **Utku DERİCİ** – 21070001031  
- **Ahmet Özgür KORKMAZ** – 21070001046  

**Academic Advisor:**  
Doç. Dr. Mete Eminağaoğlu  

---

## 🎓 Project Information

**COMP4910 – Senior Design Project**  
Yaşar University  
Computer Engineering Department  

---

## 📌 Notes

This repository contains only the Windows Client (sensor layer).  
Backend services and web dashboard components are maintained separately.

---

© 2024 AuraTwin Project Team
