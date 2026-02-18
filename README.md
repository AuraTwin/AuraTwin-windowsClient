AuraTwin Windows Client 💻
Official desktop application for AuraTwin - An Affective Digital Twin for Personalized Well-being and Self-Correction.

This repository contains the "sensor" component of the system: a lightweight Python application that runs in the background to capture and process emotional data securely.

📖 About
This is the Windows Client repository for our graduation project at Yaşar University, Computer Engineering Department. The application is designed to monitor user well-being without intruding on daily tasks. It utilizes "Capture & Release" technology to ensure privacy while providing high-frequency data for the digital twin.

🚀 Tech Stack
Python - Core application logic

OpenCV (cv2) - Camera access and image processing

PyQt5 - Modern GUI and System Tray integration

Requests - Secure communication with AWS Backend

Base64 - In-memory image encoding (Privacy-first)

✨ Key Features
🔒 Privacy-First Architecture: Images are never saved to the hard drive. They are processed entirely in RAM and sent directly to the server.

☁️ Edge Processing: Converts images to Base64 strings for secure transmission.

🤫 Background Mode: Runs silently in the System Tray (near the clock).

⚡ Smart Collision Detection: Automatically skips cycles if the camera is being used by other apps (Zoom, Meet, etc.).

🔑 Token-Based Authentication: Securely links the desktop app with the user's web dashboard.

🛠️ Installation & Setup
Clone the repository:

Bash
git clone https://github.com/KULLANICI_ADIN/AuraTwin-windowsClient.git
cd AuraTwin-windowsClient
Install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
python main.py
Configuration:

Get your App Key from the AuraTwin Dashboard.

Enter the key in the application settings.

👥 Team
Ali Haktan SIĞIN – 21070001004

Yiğit Emre ÇAY – 21070001008

Utku DERİCİ – 21070001031

Ahmet Özgür KORKMAZ – 21070001046

Academic Advisor: Doç. Dr. Mete Eminağaoğlu

🎓 Project
COMP4910 Senior Design Project
Yaşar University - Computer Engineering Department
