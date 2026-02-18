import sys
import cv2
import base64
import json
import requests
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QMessageBox, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

# --- AYARLAR ---
AWS_API_URL = "http://localhost:8000/upload" # Buraya daha sonra gerçek AWS IP'si gelecek
CONFIG_FILE = "config.json"
LOGO_FILENAME = "AuraTwin_Logo.png"  # Logo dosya adını buraya tanımladık

class AuraTwinApp(QWidget):
    def __init__(self):
        super().__init__()
        self.user_token = self.load_token()
        self.init_ui()
        self.init_tray()
        
        # 3.2. Zamanlayıcı (Timer) - Varsayılan 5 Dakika (Test için 10 saniye yaptım)
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_and_send)
        
        if self.user_token:
            self.start_background_process()

    def init_ui(self):
        self.setWindowTitle("AuraTwin İstemci")
        self.setGeometry(100, 100, 300, 200)

        if os.path.exists(LOGO_FILENAME):
            self.setWindowIcon(QIcon(LOGO_FILENAME))

        layout = QVBoxLayout()
        
        self.label = QLabel("Lütfen App Key Giriniz:")
        layout.addWidget(self.label)
        
        self.token_input = QLineEdit()
        if self.user_token:
            self.token_input.setText(self.user_token)
        layout.addWidget(self.token_input)
        
        self.btn_save = QPushButton("Kaydet ve Başlat")
        self.btn_save.clicked.connect(self.save_token_and_start)
        layout.addWidget(self.btn_save)

        self.lbl_status = QLabel("Durum: Bekleniyor...")
        layout.addWidget(self.lbl_status)
        
        self.setLayout(layout)

    def init_tray(self):
        # 3.5. System Tray Entegrasyonu
        self.tray_icon = QSystemTrayIcon(self)
        
        if os.path.exists(LOGO_FILENAME):
            # Kendi logon varsa onu kullan
            icon = QIcon(LOGO_FILENAME)
            self.tray_icon.setIcon(icon)
        else:
            # Logo dosyası yoksa PyQt'nin standart ikonunu kullan (Hata vermemesi için)
            print(f"Uyarı: {LOGO_FILENAME} bulunamadı, varsayılan ikon kullanılıyor.")
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        menu = QMenu()
        
        action_show = QAction("Göster", self)
        action_show.triggered.connect(self.show)
        menu.addAction(action_show)
        
        action_quit = QAction("Çıkış", self)
        action_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(action_quit)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def save_token_and_start(self):
        token = self.token_input.text()
        if not token:
            QMessageBox.warning(self, "Hata", "Lütfen bir anahtar girin!")
            return
            
        self.user_token = token
        with open(CONFIG_FILE, "w") as f:
            json.dump({"app_key": token}, f)
            
        self.hide() # Pencereyi gizle
        self.tray_icon.showMessage("AuraTwin", "Arka planda çalışmaya başladı.", QSystemTrayIcon.Information, 2000)
        self.start_background_process()

    def load_token(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("app_key")
        return None

    def start_background_process(self):
        self.lbl_status.setText("Durum: Arka plan aktif.")
        # 5 dakikada bir (300000 ms). Test için 10000 ms (10 sn) yapıyoruz.
        self.timer.start(10000) 
        self.capture_and_send() # Başlar başlamaz bir tane çek

    def capture_and_send(self):
        # 3.4. Güvenlik ve Gizlilik: Disk Kaydı Yok & Capture/Release
        print("Kamera açılıyor...")
        cap = cv2.VideoCapture(0) # 0: Varsayılan kamera
        
        if not cap.isOpened():
            print("Kamera başka bir uygulama (Zoom/Meet) tarafından kullanılıyor olabilir.")
            self.lbl_status.setText("Durum: Kamera meşgul.")
            return

        ret, frame = cap.read()
        cap.release() # Kamerayı hemen serbest bırak (Capture & Release)
        
        if ret:
            # Görüntüyü RAM üzerinde JPG formatına çevir
            _, buffer = cv2.imencode('.jpg', frame) #Disk Kaydı Yok
            # Base64 string'e çevir
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            # AWS'ye Gönder (Şimdilik print ediyoruz)
            print(f"Görüntü yakalandı! Boyut: {len(jpg_as_text)} karakter.")
            print(f"Token ile gönderiliyor: {self.user_token}")
            
            # BURADA REQUESTS İLE AWS'YE ATACAĞIZ (İleride açacağız)
            # try:
            #     payload = {"app_key": self.user_token, "image": jpg_as_text}
            #     requests.post(AWS_API_URL, json=payload)
            # except Exception as e:
            #     print("Sunucu hatası:", e)
        else:
            print("Görüntü alınamadı.")

# Uygulamayı Başlat
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Uygulama kapanınca (çarpıya basınca) tamamen kapanmasın, arka plana düşsün istersen:
    QApplication.setQuitOnLastWindowClosed(False) 
    
    window = AuraTwinApp()
    window.show()
    sys.exit(app.exec_())