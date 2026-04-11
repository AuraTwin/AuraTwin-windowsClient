import sys
import warnings
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")
import cv2
import base64
import json
import requests
import os
import webbrowser
from datetime import datetime, timezone
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QCheckBox, QComboBox, QDialog, QMessageBox,
                             QSystemTrayIcon, QMenu, QAction, QFrame)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt

# PyInstaller exe içinden çalışırken dosyaların yolunu doğru bul
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- SABİTLER ---
AWS_API_URL         = os.getenv("AWS_API_URL")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_API_KEY    = os.getenv("FIREBASE_API_KEY")
FIRESTORE_BASE = (
    f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}"
    f"/databases/(default)/documents"
)
CONFIG_DIR    = os.path.join(os.path.expanduser("~"), ".auratwin")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE   = os.path.join(CONFIG_DIR, "config.json")
LOGO_FILENAME = os.path.join(BASE_DIR, "AuraTwin_Logo.png")
UI_FONT       = "Segoe UI" if sys.platform == "win32" else "Helvetica Neue"
FONT_SCALE    = 1.0 if sys.platform == "win32" else 1.18

def fs(n):
    """Platform-aware font size — macOS renders Qt points smaller than Windows."""
    return round(n * FONT_SCALE)

# --- DİL SÖZLÜĞÜ ---
STRINGS = {
    "tr": {
        "subtitle":        "Well-being Asistanı",
        "prompt":          "App Key Giriniz",
        "placeholder":     "ATV-XXXX-XXXX",
        "remember":        "Beni Hatırla",
        "login_btn":       "Giriş Yap",
        "verifying_btn":   "Doğrulanıyor...",
        "register_btn":    "Hesabın yok mu? Kayıt Ol",
        "welcome":         "Hoş Geldin,\n{name}! 👋",
        "settings_btn":    "⚙  Ayarlar",
        "dashboard_btn":   "Dashboard'a Git",
        "minimize_btn":    "Sistem Tepsisine Küçült",
        "logout_btn":      "Çıkış Yap",
        # Durum mesajları
        "status_waiting":    "Bekleniyor...",
        "status_connecting": "Bağlanıyor...",
        "status_active":     "● Aktif — Analiz çalışıyor",
        "status_paused":     "⏸ Analiz duraklatıldı",
        "status_no_camera":  "● Kamera bulunamadı / meşgul",
        "status_cam_busy":   "● Kamera başka bir uygulama tarafından kullanılıyor",
        "status_no_frame":   "● Görüntü alınamadı",
        "status_conn_err":   "Bağlantı hatası.",
        "status_perm_err":   "Firestore izin hatası.",
        "status_invalid":    "Geçersiz App Key.",
        # Tray
        "tray_show":      "Göster",
        "tray_dashboard": "Dashboard'a Git",
        "tray_quit":      "Çıkış",
        "tray_waiting":   "AuraTwin — Bekleniyor",
        "tray_started":   "Arka planda çalışmaya başlandı.",
        # Ayarlar diyaloğu
        "settings_title":    "AuraTwin — Ayarlar",
        "settings_heading":  "⚙  Ayarlar",
        "interval_label":    "Analiz Aralığı (dakika)",
        "interval_suffix":   " dk",
        "interval_note":     (
            "💡  Tavsiye edilen aralık: 5 dakika\n"
            "Fotoğraflar ne sıklıkla çekilirse dijital ikizin\n"
            "o kadar doğru ve kişiselleşmiş olur."
        ),
        "analysis_label":  "Analiz Durumu",
        "pause_btn":       "⏸  Analizi Durdur",
        "resume_btn":      "▶  Analizi Başlat",
        "lang_label":      "Dil / Language",
        "save_btn":        "Kaydet",
        # Mesaj kutuları
        "err_no_key":       "Lütfen bir App Key girin!",
        "err_conn_title":   "Bağlantı Hatası",
        "err_conn_msg":     "Sunucuya ulaşılamadı. İnternet bağlantınızı kontrol edin.",
        "err_perm_title":   "Firestore İzin Hatası",
        "err_perm_msg":     (
            "Firestore Security Rules okuma iznine izin vermiyor.\n"
            "Firebase Console → Firestore → Rules bölümünü kontrol edin."
        ),
        "err_invalid_title": "Geçersiz Key",
        "err_invalid_msg":   (
            "Bu App Key sistemde bulunamadı.\n"
            "Web panelinden doğru key'i kopyaladığınızdan emin olun."
        ),
        # Test penceresi
        "test_btn":           "🎯  Test Et",
        "test_title":         "AuraTwin — Kamera Testi",
        "test_heading":       "Kamera Testi",
        "test_send_btn":      "📸  Çek & Gönder",
        "test_no_camera":     "Kamera açılamadı.",
        "test_sending":       "Gönderiliyor...",
        "test_sent":          "✅  Gönderildi! Sonucu Dashboard'dan takip edin.",
        "test_error":         "❌  Gönderim hatası. Bağlantıyı kontrol edin.",
    },
    "en": {
        "subtitle":        "Well-being Assistant",
        "prompt":          "Enter App Key",
        "placeholder":     "ATV-XXXX-XXXX",
        "remember":        "Remember Me",
        "login_btn":       "Sign In",
        "verifying_btn":   "Verifying...",
        "register_btn":    "No account? Register",
        "welcome":         "Welcome,\n{name}! 👋",
        "settings_btn":    "⚙  Settings",
        "dashboard_btn":   "Go to Dashboard",
        "minimize_btn":    "Minimize to Tray",
        "logout_btn":      "Log Out",
        # Status messages
        "status_waiting":    "Waiting...",
        "status_connecting": "Connecting...",
        "status_active":     "● Active — Analysis running",
        "status_paused":     "⏸ Analysis paused",
        "status_no_camera":  "● Camera not found / busy",
        "status_cam_busy":   "● Camera is being used by another application",
        "status_no_frame":   "● Could not capture image",
        "status_conn_err":   "Connection error.",
        "status_perm_err":   "Firestore permission error.",
        "status_invalid":    "Invalid App Key.",
        # Tray
        "tray_show":      "Show",
        "tray_dashboard": "Go to Dashboard",
        "tray_quit":      "Quit",
        "tray_waiting":   "AuraTwin — Waiting",
        "tray_started":   "Started running in the background.",
        # Settings dialog
        "settings_title":    "AuraTwin — Settings",
        "settings_heading":  "⚙  Settings",
        "interval_label":    "Analysis Interval (minutes)",
        "interval_suffix":   " min",
        "interval_note":     (
            "💡  Recommended interval: 5 minutes\n"
            "The more frequently photos are taken,\n"
            "the more accurate your digital twin becomes."
        ),
        "analysis_label":  "Analysis Status",
        "pause_btn":       "⏸  Pause Analysis",
        "resume_btn":      "▶  Start Analysis",
        "lang_label":      "Language",
        "save_btn":        "Save",
        # Message boxes
        "err_no_key":       "Please enter an App Key!",
        "err_conn_title":   "Connection Error",
        "err_conn_msg":     "Could not reach the server. Please check your internet connection.",
        "err_perm_title":   "Firestore Permission Error",
        "err_perm_msg":     (
            "Firestore Security Rules are blocking read access.\n"
            "Check Firebase Console → Firestore → Rules."
        ),
        "err_invalid_title": "Invalid Key",
        "err_invalid_msg":   (
            "This App Key was not found in the system.\n"
            "Make sure you copied the correct key from the web panel."
        ),
        # Test window
        "test_btn":           "🎯  Test",
        "test_title":         "AuraTwin — Camera Test",
        "test_heading":       "Camera Test",
        "test_send_btn":      "📸  Capture & Send",
        "test_no_camera":     "Could not open camera.",
        "test_sending":       "Sending...",
        "test_sent":          "✅  Sent! Check Dashboard for results.",
        "test_error":         "❌  Send error. Check your connection.",
    },
}

# --- FIREBASE YARDIMCI FONKSİYONLAR ---

def firestore_get(doc_path):
    url = f"{FIRESTORE_BASE}/{doc_path}?key={FIREBASE_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        print(f"[Firestore] GET {doc_path} → {resp.status_code}")
        if resp.status_code == 200:
            return resp.status_code, resp.json()
        return resp.status_code, None
    except requests.RequestException as e:
        print(f"[Firestore] Bağlantı hatası: {e}")
        return -1, None


def get_string(doc, field):
    return doc.get("fields", {}).get(field, {}).get("stringValue")


def validate_app_key(app_key):
    status, key_doc = firestore_get(f"app_keys/{app_key}")
    if status == -1:
        return "connection_error"
    if status == 403:
        return "permission_error"
    if status == 404 or key_doc is None:
        return None

    uid = get_string(key_doc, "uid")
    if not uid:
        return None

    status2, profile_doc = firestore_get(f"users/{uid}/profile/data")
    if status2 == 403:
        return "permission_error"
    if status2 != 200 or profile_doc is None:
        return "connection_error"

    return {
        "uid":     uid,
        "name":    get_string(profile_doc, "name") or "",
        "surname": get_string(profile_doc, "surname") or "",
    }


# --- MESAJ KUTUSU YARDIMCISI ---

def show_msgbox(parent, icon, title, text):
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setIcon(icon)
    box.setStyleSheet(
        "QLabel { color: #111111; }"
        "QPushButton { color: #111111; }"
    )
    box.exec_()


# --- TEST DİYALOĞU ---

class TestDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.main = parent
        self._current_frame = None
        self.cap = None
        self.cam_timer = QTimer()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedWidth(480)
        if os.path.exists(LOGO_FILENAME):
            self.setWindowIcon(QIcon(LOGO_FILENAME))
        self.setWindowTitle(self.main.t("test_title"))
        self.setStyleSheet("background-color: #F5F3FF;")

        outer = QVBoxLayout()
        outer.setContentsMargins(20, 16, 20, 16)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 16px; }")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 14, 12, 18)
        layout.setSpacing(10)

        lbl_title = QLabel(self.main.t("test_heading"))
        lbl_title.setFont(QFont(UI_FONT, fs(15), QFont.Bold))
        lbl_title.setStyleSheet("color: #4C1D95;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        # Kamera görüntüsü — 16:9
        # Dialog 480 - outer(20+20) - card(12+12) = 416px genişlik, yükseklik 416*9/16=234
        cam_w, cam_h = 416, 234
        self.lbl_camera = QLabel()
        self.lbl_camera.setFixedSize(cam_w, cam_h)
        self.lbl_camera.setAlignment(Qt.AlignCenter)
        self.lbl_camera.setStyleSheet(
            "background-color: #1E1B4B; border-radius: 14px; color: #9CA3AF;"
        )
        self.lbl_camera.setText("📷")
        self.lbl_camera.setFont(QFont(UI_FONT, fs(32)))
        layout.addWidget(self.lbl_camera)

        # Durum etiketi
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setFont(QFont(UI_FONT, fs(9)))
        self.lbl_status.setStyleSheet("color: #6B7280;")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        # Çek & Gönder butonu
        self.btn_send = QPushButton(self.main.t("test_send_btn"))
        self.btn_send.setFixedHeight(48)
        self.btn_send.setFont(QFont(UI_FONT, fs(11), QFont.Bold))
        self.btn_send.setCursor(Qt.PointingHandCursor)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #7C3AED; color: white;
                border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #6D28D9; }
            QPushButton:pressed { background-color: #5B21B6; }
            QPushButton:disabled { background-color: #C4B5FD; }
        """)
        self.btn_send.clicked.connect(self._capture_and_send)
        layout.addWidget(self.btn_send)

        outer.addWidget(card)
        self.setLayout(outer)

        self.adjustSize()
        geo = parent.frameGeometry()
        self.move(
            geo.x() + (geo.width() - self.width()) // 2,
            geo.y() + (geo.height() - self.height()) // 2,
        )

        self._start_camera()

    def _start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.lbl_camera.setText(self.main.t("test_no_camera"))
            self.btn_send.setEnabled(False)
            return
        self.cam_timer.timeout.connect(self._update_frame)
        self.cam_timer.start(33)

    @staticmethod
    def _rounded_pixmap(pixmap, radius=14):
        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)
        p = QPainter(result)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)
        p.setClipPath(path)
        p.drawPixmap(0, 0, pixmap)
        p.end()
        return result

    def _update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        self._current_frame = frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        qt_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        scaled = QPixmap.fromImage(qt_img).scaled(
            416, 234, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        ).copy(0, 0, 416, 234)
        self.lbl_camera.setPixmap(self._rounded_pixmap(scaled))

    def _capture_and_send(self):
        if self._current_frame is None:
            return
        self.btn_send.setEnabled(False)
        self.lbl_status.setStyleSheet("color: #3B82F6;")
        self.lbl_status.setText(self.main.t("test_sending"))
        QApplication.processEvents()

        _, buffer = cv2.imencode('.jpg', self._current_frame)
        jpg_b64 = base64.b64encode(buffer).decode('utf-8')
        try:
            payload = {
                "app_key":   self.main.config.get("app_key"),
                "image":     jpg_b64,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            response = requests.post(AWS_API_URL, json=payload, timeout=15)
            if response.status_code == 200:
                self.lbl_status.setStyleSheet("color: #10B981; font-weight: bold;")
                self.lbl_status.setText(self.main.t("test_sent"))
            else:
                self.lbl_status.setStyleSheet("color: #EF4444; font-weight: bold;")
                self.lbl_status.setText(self.main.t("test_error"))
        except requests.RequestException:
            self.lbl_status.setStyleSheet("color: #EF4444; font-weight: bold;")
            self.lbl_status.setText(self.main.t("test_error"))
        finally:
            self.btn_send.setEnabled(True)

    def closeEvent(self, event):
        self.cam_timer.stop()
        if self.cap:
            self.cap.release()
        super().closeEvent(event)


# --- AYARLAR DİYALOĞU ---

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.main = parent
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedWidth(400)

        if os.path.exists(LOGO_FILENAME):
            self.setWindowIcon(QIcon(LOGO_FILENAME))

        self.setStyleSheet("background-color: #F5F3FF;")

        outer = QVBoxLayout()
        outer.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 16px; }")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 28, 24, 24)
        layout.setSpacing(16)

        # Başlık
        self.lbl_title = QLabel()
        self.lbl_title.setFont(QFont(UI_FONT, fs(15), QFont.Bold))
        self.lbl_title.setStyleSheet("color: #4C1D95;")
        layout.addWidget(self.lbl_title)

        self._sep(layout)

        # Analiz Aralığı
        self.lbl_interval = QLabel()
        self.lbl_interval.setFont(QFont(UI_FONT, fs(10), QFont.Bold))
        self.lbl_interval.setStyleSheet("color: #374151;")
        layout.addWidget(self.lbl_interval)

        self._interval_options = [1, 2, 5, 10, 30, 60]
        current_interval = self.main.config.get("interval_minutes", 5)

        combo_wrapper = QFrame()
        combo_wrapper.setFixedHeight(40)
        combo_wrapper.setStyleSheet("""
            QFrame {
                border: 2px solid #DDD6FE; border-radius: 10px;
                background: #FAFAFA;
            }
        """)
        combo_inner = QHBoxLayout(combo_wrapper)
        combo_inner.setContentsMargins(4, 0, 0, 0)
        combo_inner.setSpacing(0)

        self.combo_interval = QComboBox()
        suffix = "dk" if self.main.lang == "tr" else "min"
        for val in self._interval_options:
            self.combo_interval.addItem(f"  {val} {suffix}", val)
        idx = self._interval_options.index(current_interval) if current_interval in self._interval_options else 2
        self.combo_interval.setCurrentIndex(idx)
        self.combo_interval.setFont(QFont(UI_FONT, fs(11)))
        self.combo_interval.setMaxVisibleItems(4)
        self.combo_interval.setStyleSheet("""
            QComboBox {
                border: none; background: transparent;
                color: #1E1B4B; padding: 0 4px;
            }
            QComboBox::drop-down { width: 0px; border: none; }
            QComboBox QAbstractItemView {
                border: 2px solid #DDD6FE; border-radius: 8px;
                background: #FFFFFF; selection-background-color: #EDE9FE;
                selection-color: #4C1D95; color: #1E1B4B;
            }
        """)
        combo_inner.addWidget(self.combo_interval)

        lbl_arrow = QLabel("▼")
        lbl_arrow.setFixedWidth(32)
        lbl_arrow.setAlignment(Qt.AlignCenter)
        lbl_arrow.setFont(QFont(UI_FONT, fs(9)))
        lbl_arrow.setStyleSheet("color: #7C3AED; border: none; background: transparent;")
        combo_inner.addWidget(lbl_arrow)

        layout.addWidget(combo_wrapper)

        self.lbl_note = QLabel()
        self.lbl_note.setFont(QFont(UI_FONT, fs(9)))
        self.lbl_note.setStyleSheet(
            "color: #6B7280; background-color: #F5F3FF; border-radius: 8px; padding: 10px;"
        )
        self.lbl_note.setWordWrap(True)
        layout.addWidget(self.lbl_note)

        self._sep(layout)

        # Analiz Durumu
        self.lbl_analysis = QLabel()
        self.lbl_analysis.setFont(QFont(UI_FONT, fs(10), QFont.Bold))
        self.lbl_analysis.setStyleSheet("color: #374151;")
        layout.addWidget(self.lbl_analysis)

        self.btn_toggle = QPushButton()
        self.btn_toggle.setFixedHeight(44)
        self.btn_toggle.setFont(QFont(UI_FONT, fs(10), QFont.Bold))
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_analysis)
        layout.addWidget(self.btn_toggle)

        self._sep(layout)

        # Dil Seçimi
        self.lbl_lang = QLabel()
        self.lbl_lang.setFont(QFont(UI_FONT, fs(10), QFont.Bold))
        self.lbl_lang.setStyleSheet("color: #374151;")
        layout.addWidget(self.lbl_lang)

        lang_row = QHBoxLayout()
        self.btn_lang_tr = QPushButton("🇹🇷  Türkçe")
        self.btn_lang_en = QPushButton("🇬🇧  English")
        for btn in (self.btn_lang_tr, self.btn_lang_en):
            btn.setFixedHeight(38)
            btn.setFont(QFont(UI_FONT, fs(10)))
            btn.setCursor(Qt.PointingHandCursor)
        self.btn_lang_tr.clicked.connect(lambda: self._change_lang("tr"))
        self.btn_lang_en.clicked.connect(lambda: self._change_lang("en"))
        lang_row.addWidget(self.btn_lang_tr)
        lang_row.addWidget(self.btn_lang_en)
        layout.addLayout(lang_row)

        layout.addStretch()

        # Kaydet
        self.btn_save = QPushButton()
        self.btn_save.setFixedHeight(44)
        self.btn_save.setFont(QFont(UI_FONT, fs(11), QFont.Bold))
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #7C3AED; color: white;
                border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #6D28D9; }
            QPushButton:pressed { background-color: #5B21B6; }
        """)
        self.btn_save.clicked.connect(self.save_and_close)
        layout.addWidget(self.btn_save)

        outer.addWidget(card)
        self.setLayout(outer)

        # Metinleri ve toggle'ı uygula
        self._apply_texts()
        self._update_toggle_btn()
        self._update_lang_btns()

        self.adjustSize()
        geo = parent.frameGeometry()
        self.move(
            geo.x() + (geo.width() - self.width()) // 2,
            geo.y() + (geo.height() - self.height()) // 2,
        )

    def _sep(self, layout):
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #EDE9FE;")
        layout.addWidget(sep)

    def _apply_texts(self):
        t = self.main.t
        self.setWindowTitle(t("settings_title"))
        self.lbl_title.setText(t("settings_heading"))
        self.lbl_interval.setText(t("interval_label"))
        self.lbl_note.setText(t("interval_note"))
        self.lbl_analysis.setText(t("analysis_label"))
        self.lbl_lang.setText(t("lang_label"))
        self.btn_save.setText(t("save_btn"))
        self._update_toggle_btn()

    def _update_toggle_btn(self):
        t = self.main.t
        if self.main.is_paused:
            self.btn_toggle.setText(t("resume_btn"))
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #10B981; color: white;
                    border-radius: 10px; border: none;
                }
                QPushButton:hover { background-color: #059669; }
            """)
        else:
            self.btn_toggle.setText(t("pause_btn"))
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #F59E0B;
                    border: 2px solid #FDE68A; border-radius: 10px;
                }
                QPushButton:hover { background-color: #FFFBEB; border-color: #F59E0B; }
            """)

    def _update_lang_btns(self):
        active = """
            QPushButton {
                background-color: #7C3AED; color: white;
                border-radius: 8px; border: none;
            }
        """
        inactive = """
            QPushButton {
                background-color: transparent; color: #9CA3AF;
                border: 2px solid #E5E7EB; border-radius: 8px;
            }
            QPushButton:hover { border-color: #7C3AED; color: #7C3AED; }
        """
        lang = self.main.lang
        self.btn_lang_tr.setStyleSheet(active if lang == "tr" else inactive)
        self.btn_lang_en.setStyleSheet(active if lang == "en" else inactive)

    def _change_lang(self, lang):
        self.main.apply_language(lang)
        self._apply_texts()
        self._update_lang_btns()

    def toggle_analysis(self):
        if self.main.is_paused:
            self.main.resume_analysis()
        else:
            self.main.pause_analysis()
        self._update_toggle_btn()

    def save_and_close(self):
        minutes = self.combo_interval.currentData()
        self.main.config["interval_minutes"] = minutes
        self.main.save_config()
        if not self.main.is_paused:
            self.main.timer.start(minutes * 60 * 1000)
        self.accept()


# --- WORKER THREAD'LER ---

class LoginWorker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, app_key):
        super().__init__()
        self.app_key = app_key

    def run(self):
        result = validate_app_key(self.app_key)
        self.finished.emit(result)


class CaptureWorker(QThread):
    status_update = pyqtSignal(str, str)

    def __init__(self, app_key, aws_url):
        super().__init__()
        self.app_key = app_key
        self.aws_url = aws_url

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Kamera açılamadı.")
            self.status_update.emit("status_no_camera", "error")
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Görüntü alınamadı.")
            self.status_update.emit("status_no_frame", "error")
            return

        if frame.mean() < 5:
            print("Kamera meşgul (siyah frame) — bu periyot pas geçildi.")
            self.status_update.emit("status_cam_busy", "warning")
            return

        _, buffer = cv2.imencode('.jpg', frame)
        jpg_b64 = base64.b64encode(buffer).decode('utf-8')
        print(f"Görüntü yakalandı! Boyut: {len(jpg_b64)} karakter.")

        try:
            payload = {
                "app_key":   self.app_key,
                "image":     jpg_b64,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            response = requests.post(self.aws_url, json=payload, timeout=15)
            print(f"AWS yanıtı: {response.status_code} — {response.text[:200]}")
            if response.status_code == 200:
                self.status_update.emit("status_active", "success")
            else:
                self.status_update.emit("status_conn_err", "error")
        except requests.RequestException as e:
            print(f"AWS bağlantı hatası: {e}")
            self.status_update.emit("status_conn_err", "error")


# --- ANA UYGULAMA ---

class AuraTwinApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.lang = self.config.get("lang", "tr")
        self._status_key   = "status_waiting"
        self._status_level = "idle"

        self.init_ui()
        self.init_tray()

        self.is_paused = False
        self._login_worker   = None
        self._capture_worker = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_and_send)

        if (self.config.get("remember_me")
                and self.config.get("app_key")
                and self.config.get("uid")):
            QTimer.singleShot(0, self._auto_login)

        self._center_window()

    # --- YARDIMCI ---

    def t(self, key):
        return STRINGS.get(self.lang, STRINGS["tr"]).get(key, key)

    def apply_language(self, lang):
        self.lang = lang
        self.config["lang"] = lang
        self.save_config()

        # Login ekranı
        self.lbl_prompt.setText(self.t("prompt"))
        self.token_input.setPlaceholderText(self.t("placeholder"))
        self.chk_remember.setText(self.t("remember"))
        self.btn_save.setText(self.t("login_btn"))
        self.btn_register.setText(self.t("register_btn"))
        # Subtitle (durum ekranı)
        self.lbl_sub.setText(self.t("subtitle"))
        # Durum ekranı
        self.btn_settings.setText(self.t("settings_btn"))
        self.btn_test.setText(self.t("test_btn"))
        self.btn_dashboard.setText(self.t("dashboard_btn"))
        self.btn_minimize.setText(self.t("minimize_btn"))
        self.btn_logout.setText(self.t("logout_btn"))
        # Hoş geldin mesajı (gösteriliyorsa)
        name    = self.config.get("name", "")
        surname = self.config.get("surname", "")
        if name or surname:
            full_name = f"{name} {surname}".strip()
            self.lbl_welcome.setText(self.t("welcome").format(name=full_name))
        # Durum etiketi
        self.set_status(self._status_key, self._status_level)
        # Tray
        self.action_show.setText(self.t("tray_show"))
        self.action_dashboard.setText(self.t("tray_dashboard"))
        self.action_quit.setText(self.t("tray_quit"))
        # Dil butonları (login ekranı)
        self._update_login_lang_btns()

    def _update_login_lang_btns(self):
        active = """
            QPushButton {
                background-color: #7C3AED; color: white;
                border-radius: 8px; border: none; padding: 0 8px;
            }
        """
        inactive = """
            QPushButton {
                background-color: transparent; color: #7C3AED;
                border: none; padding: 0 8px;
            }
            QPushButton:hover { background-color: #DDD6FE; border-radius: 8px; }
        """
        self.btn_lang_tr.setStyleSheet(active if self.lang == "tr" else inactive)
        self.btn_lang_en.setStyleSheet(active if self.lang == "en" else inactive)

    def eventFilter(self, obj, event):
        if obj is self.token_input:
            if event.type() == QEvent.FocusIn:
                self._input_frame.setStyleSheet(
                    "QFrame#inputFrame { border: 2px solid #7C3AED; background: #FFFFFF; border-radius: 10px; }"
                )
            elif event.type() == QEvent.FocusOut:
                self._input_frame.setStyleSheet(
                    "QFrame#inputFrame { border: 2px solid #DDD6FE; background: #FAFAFA; border-radius: 10px; }"
                )
        return super().eventFilter(obj, event)

    def _center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )

    def _auto_login(self):
        name    = self.config.get("name", "")
        surname = self.config.get("surname", "")
        full_name = f"{name} {surname}".strip()
        self.tray_icon.setToolTip(f"AuraTwin — {full_name}")
        self.show_status_screen(name, surname)
        self.set_status("status_active", "success")
        self.start_background_process()

    def set_status(self, key, level="idle"):
        self._status_key   = key
        self._status_level = level
        colors = {
            "idle":    "#9CA3AF",
            "info":    "#3B82F6",
            "success": "#10B981",
            "error":   "#EF4444",
            "warning": "#F59E0B",
        }
        color = colors.get(level, "#9CA3AF")
        self.lbl_status.setStyleSheet(
            f"color: {color}; font-weight: bold; margin-top: 4px;"
        )
        self.lbl_status.setText(self.t(key))

    # --- UI ---

    def init_ui(self):
        self.setWindowTitle("AuraTwin")
        self.setFixedWidth(400)

        if os.path.exists(LOGO_FILENAME):
            self.setWindowIcon(QIcon(LOGO_FILENAME))

        self.setStyleSheet("background-color: #F5F3FF;")

        outer = QVBoxLayout()
        outer.setContentsMargins(30, 30, 30, 30)
        outer.setSpacing(0)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 16px; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 32, 28, 28)
        cl.setSpacing(14)

        # Logo
        if os.path.exists(LOGO_FILENAME):
            lbl_logo = QLabel()
            lbl_logo.setPixmap(
                QPixmap(LOGO_FILENAME).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            lbl_logo.setAlignment(Qt.AlignCenter)
            cl.addWidget(lbl_logo)

        # Başlık
        lbl_title = QLabel("AuraTwin")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setFont(QFont(UI_FONT, fs(22), QFont.Bold))
        lbl_title.setStyleSheet("color: #4C1D95;")
        cl.addWidget(lbl_title)

        # Subtitle — sadece durum ekranında, ortalı, TR/EN duyarlı
        self.lbl_sub = QLabel(self.t("subtitle"))
        self.lbl_sub.setFont(QFont(UI_FONT, fs(10)))
        self.lbl_sub.setStyleSheet("color: #7C3AED;")
        self.lbl_sub.setAlignment(Qt.AlignCenter)
        self.lbl_sub.hide()
        cl.addWidget(self.lbl_sub)

        # TR/EN pill toggle — sadece giriş ekranında, ortalı
        self.lang_toggle_widget = QFrame()
        self.lang_toggle_widget.setStyleSheet(
            "QFrame { background: #EDE9FE; border-radius: 10px; }"
        )
        pill_layout = QHBoxLayout(self.lang_toggle_widget)
        pill_layout.setContentsMargins(3, 3, 3, 3)
        pill_layout.setSpacing(2)

        self.btn_lang_tr = QPushButton("TR")
        self.btn_lang_en = QPushButton("EN")
        for btn in (self.btn_lang_tr, self.btn_lang_en):
            btn.setFixedHeight(30)
            btn.setMinimumWidth(54)
            btn.setFont(QFont(UI_FONT, fs(9), QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
        self.btn_lang_tr.clicked.connect(lambda: self.apply_language("tr"))
        self.btn_lang_en.clicked.connect(lambda: self.apply_language("en"))
        pill_layout.addWidget(self.btn_lang_tr)
        pill_layout.addWidget(self.btn_lang_en)

        pill_center = QHBoxLayout()
        pill_center.addStretch()
        pill_center.addWidget(self.lang_toggle_widget)
        pill_center.addStretch()
        cl.addLayout(pill_center)

        self._update_login_lang_btns()

        # Ayırıcı
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #EDE9FE;")
        cl.addWidget(line)

        # --- GİRİŞ EKRANI ---
        self.lbl_prompt = QLabel(self.t("prompt"))
        self.lbl_prompt.setAlignment(Qt.AlignCenter)
        self.lbl_prompt.setFont(QFont(UI_FONT, fs(10)))
        self.lbl_prompt.setStyleSheet("color: #374151; margin-top: 4px;")
        cl.addWidget(self.lbl_prompt)

        self._input_frame = QFrame()
        self._input_frame.setObjectName("inputFrame")
        self._input_frame.setFixedHeight(44)
        self._input_frame.setStyleSheet(
            "QFrame#inputFrame { border: 2px solid #DDD6FE; border-radius: 10px; background: #FAFAFA; }"
        )
        input_row = QHBoxLayout(self._input_frame)
        input_row.setContentsMargins(6, 0, 4, 0)
        input_row.setSpacing(0)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText(self.t("placeholder"))
        self.token_input.setFont(QFont(UI_FONT, fs(11)))
        self.token_input.setAlignment(Qt.AlignCenter)
        self.token_input.setStyleSheet(
            "QLineEdit { border: none; background: transparent; color: #1E1B4B; padding: 0 4px; }"
        )
        self.token_input.returnPressed.connect(self.on_save_clicked)
        self.token_input.installEventFilter(self)
        if self.config.get("app_key"):
            self.token_input.setText(self.config["app_key"])

        btn_paste = QPushButton("📋")
        btn_paste.setFixedSize(32, 32)
        btn_paste.setFont(QFont(UI_FONT, fs(13)))
        btn_paste.setCursor(Qt.PointingHandCursor)
        btn_paste.setToolTip("Panodan yapıştır")
        btn_paste.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #C4B5FD; border-radius: 6px; }
            QPushButton:hover { background: #EDE9FE; color: #7C3AED; }
            QPushButton:pressed { background: #DDD6FE; }
        """)
        btn_paste.clicked.connect(
            lambda: self.token_input.setText(QApplication.clipboard().text().strip())
        )

        input_row.addWidget(self.token_input)
        input_row.addWidget(btn_paste)
        cl.addWidget(self._input_frame)

        self.chk_remember = QCheckBox(self.t("remember"))
        self.chk_remember.setFont(QFont(UI_FONT, fs(9)))
        self.chk_remember.setStyleSheet("""
            QCheckBox { color: #6B7280; spacing: 6px; }
            QCheckBox::indicator {
                width: 16px; height: 16px; border-radius: 4px; border: 2px solid #DDD6FE;
            }
            QCheckBox::indicator:checked { background-color: #7C3AED; border-color: #7C3AED; }
        """)
        self.chk_remember.setChecked(self.config.get("remember_me", False))
        cl.addWidget(self.chk_remember)

        self.btn_save = QPushButton(self.t("login_btn"))
        self.btn_save.setFixedHeight(44)
        self.btn_save.setFont(QFont(UI_FONT, fs(11), QFont.Bold))
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #7C3AED; color: white;
                border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #6D28D9; }
            QPushButton:pressed { background-color: #5B21B6; }
            QPushButton:disabled { background-color: #C4B5FD; }
        """)
        self.btn_save.clicked.connect(self.on_save_clicked)
        cl.addWidget(self.btn_save)

        self.btn_register = QPushButton(self.t("register_btn"))
        self.btn_register.setFixedHeight(40)
        self.btn_register.setFont(QFont(UI_FONT, fs(10)))
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #7C3AED;
                border: 2px solid #DDD6FE; border-radius: 10px;
            }
            QPushButton:hover { background-color: #F5F3FF; border-color: #7C3AED; }
        """)
        self.btn_register.clicked.connect(
            lambda: webbrowser.open("https://auratwin.netlify.app/register")
        )
        cl.addWidget(self.btn_register)

        # --- DURUM EKRANI (gizli) ---
        self.lbl_welcome = QLabel("")
        self.lbl_welcome.setAlignment(Qt.AlignCenter)
        self.lbl_welcome.setFont(QFont(UI_FONT, fs(13), QFont.Bold))
        self.lbl_welcome.setStyleSheet("color: #4C1D95;")
        self.lbl_welcome.setWordWrap(True)
        self.lbl_welcome.hide()
        cl.addWidget(self.lbl_welcome)

        self.btn_settings = QPushButton(self.t("settings_btn"))
        self.btn_settings.setFixedHeight(40)
        self.btn_settings.setFont(QFont(UI_FONT, fs(10)))
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #6B7280;
                border: 2px solid #E5E7EB; border-radius: 10px;
            }
            QPushButton:hover { background-color: #F9FAFB; border-color: #9CA3AF; color: #374151; }
        """)
        self.btn_settings.clicked.connect(lambda: SettingsDialog(self).exec_())
        self.btn_settings.hide()
        cl.addWidget(self.btn_settings)

        self.btn_test = QPushButton(self.t("test_btn"))
        self.btn_test.setFixedHeight(44)
        self.btn_test.setFont(QFont(UI_FONT, fs(10), QFont.Bold))
        self.btn_test.setCursor(Qt.PointingHandCursor)
        self.btn_test.setStyleSheet("""
            QPushButton {
                background-color: #4C1D95; color: white;
                border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #3B0764; }
            QPushButton:pressed { background-color: #2E1065; }
        """)
        self.btn_test.clicked.connect(lambda: TestDialog(self).exec_())
        self.btn_test.hide()
        cl.addWidget(self.btn_test)

        self.btn_dashboard = QPushButton(self.t("dashboard_btn"))
        self.btn_dashboard.setFixedHeight(44)
        self.btn_dashboard.setFont(QFont(UI_FONT, fs(10), QFont.Bold))
        self.btn_dashboard.setCursor(Qt.PointingHandCursor)
        self.btn_dashboard.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #7C3AED;
                border: 2px solid #DDD6FE; border-radius: 10px;
            }
            QPushButton:hover { background-color: #F5F3FF; border-color: #7C3AED; }
        """)
        self.btn_dashboard.clicked.connect(
            lambda: webbrowser.open("https://auratwin.netlify.app/")
        )
        self.btn_dashboard.hide()
        cl.addWidget(self.btn_dashboard)

        self.btn_minimize = QPushButton(self.t("minimize_btn"))
        self.btn_minimize.setFixedHeight(44)
        self.btn_minimize.setFont(QFont(UI_FONT, fs(10), QFont.Bold))
        self.btn_minimize.setCursor(Qt.PointingHandCursor)
        self.btn_minimize.setStyleSheet("""
            QPushButton {
                background-color: #7C3AED; color: white;
                border-radius: 10px; border: none;
            }
            QPushButton:hover { background-color: #6D28D9; }
        """)
        self.btn_minimize.clicked.connect(self.hide)
        self.btn_minimize.hide()
        cl.addWidget(self.btn_minimize)

        self.btn_logout = QPushButton(self.t("logout_btn"))
        self.btn_logout.setFixedHeight(40)
        self.btn_logout.setFont(QFont(UI_FONT, fs(10)))
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #EF4444;
                border: 2px solid #FECACA; border-radius: 10px;
            }
            QPushButton:hover { background-color: #FEF2F2; border-color: #EF4444; }
        """)
        self.btn_logout.clicked.connect(self.logout)
        self.btn_logout.hide()
        cl.addWidget(self.btn_logout)

        # Durum etiketi
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setFont(QFont(UI_FONT, fs(9)))
        self.lbl_status.setStyleSheet("color: #9CA3AF; margin-top: 4px;")
        cl.addWidget(self.lbl_status)
        self.set_status("status_waiting", "idle")

        outer.addWidget(card)
        self.setLayout(outer)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)

        if os.path.exists(LOGO_FILENAME):
            self.tray_icon.setIcon(QIcon(LOGO_FILENAME))
        else:
            self.tray_icon.setIcon(
                QApplication.style().standardIcon(QApplication.style().SP_ComputerIcon)
            )

        menu = QMenu()

        self.action_show = QAction(self.t("tray_show"), self)
        self.action_show.triggered.connect(self.show)
        menu.addAction(self.action_show)

        self.action_dashboard = QAction(self.t("tray_dashboard"), self)
        self.action_dashboard.triggered.connect(
            lambda: webbrowser.open("https://auratwin.netlify.app/")
        )
        menu.addAction(self.action_dashboard)

        menu.addSeparator()

        self.action_quit = QAction(self.t("tray_quit"), self)
        self.action_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(self.action_quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip(self.t("tray_waiting"))
        self.tray_icon.show()

    def show_status_screen(self, name, surname):
        full_name = f"{name} {surname}".strip()

        self.lbl_prompt.hide()
        self._input_frame.hide()
        self.chk_remember.hide()
        self.btn_save.hide()
        self.btn_register.hide()
        self.lang_toggle_widget.hide()

        self.lbl_sub.setText(self.t("subtitle"))
        self.lbl_sub.show()
        self.lbl_welcome.setText(self.t("welcome").format(name=full_name))
        self.lbl_welcome.show()
        self.btn_settings.show()
        self.btn_test.show()
        self.btn_dashboard.show()
        self.btn_minimize.show()
        self.btn_logout.show()

        self.setMaximumHeight(16777215)
        self.adjustSize()
        self._center_window()

    def logout(self):
        self.timer.stop()
        self.lang = self.config.get("lang", "tr")   # dil tercihini koru
        self.config = {"lang": self.lang}
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

        self.lbl_welcome.hide()
        self.lbl_sub.hide()
        self.btn_settings.hide()
        self.btn_test.hide()
        self.btn_dashboard.hide()
        self.btn_minimize.hide()
        self.btn_logout.hide()

        self.token_input.clear()
        self.chk_remember.setChecked(False)
        self.lbl_prompt.show()
        self._input_frame.show()
        self.chk_remember.show()
        self.btn_save.show()
        self.btn_register.show()
        self.lang_toggle_widget.show()
        self._update_login_lang_btns()

        self.tray_icon.setToolTip(self.t("tray_waiting"))
        self.set_status("status_waiting", "idle")

        self.setMaximumHeight(16777215)
        self.adjustSize()
        self._center_window()
        self.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # --- TOKEN DOĞRULAMA ---

    def on_save_clicked(self):
        app_key = self.token_input.text().strip()
        if not app_key:
            show_msgbox(self, QMessageBox.Warning, "AuraTwin", self.t("err_no_key"))
            return

        self.btn_save.setEnabled(False)
        self.btn_save.setText(self.t("verifying_btn"))
        self.set_status("status_connecting", "info")

        self._login_worker = LoginWorker(app_key)
        self._login_worker.finished.connect(self._on_login_result)
        self._login_worker.start()

    def _on_login_result(self, result):
        self.btn_save.setEnabled(True)
        self.btn_save.setText(self.t("login_btn"))

        if result == "connection_error":
            self.set_status("status_conn_err", "error")
            show_msgbox(self, QMessageBox.Critical, self.t("err_conn_title"), self.t("err_conn_msg"))
            return

        if result == "permission_error":
            self.set_status("status_perm_err", "error")
            show_msgbox(self, QMessageBox.Critical, self.t("err_perm_title"), self.t("err_perm_msg"))
            return

        if result is None:
            self.set_status("status_invalid", "error")
            show_msgbox(self, QMessageBox.Warning, self.t("err_invalid_title"), self.t("err_invalid_msg"))
            return

        app_key = self._login_worker.app_key
        self.config = {
            "app_key":          app_key,
            "uid":              result["uid"],
            "name":             result["name"],
            "surname":          result["surname"],
            "remember_me":      self.chk_remember.isChecked(),
            "lang":             self.lang,
            "interval_minutes": self.config.get("interval_minutes", 5),
        }
        self.save_config()

        full_name = f"{result['name']} {result['surname']}".strip()
        self.tray_icon.setToolTip(f"AuraTwin — {full_name}")
        self.show_status_screen(result["name"], result["surname"])
        self.set_status("status_active", "success")
        self.start_background_process()

    # --- CONFIG ---

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def save_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    # --- ARKA PLAN ---

    def pause_analysis(self):
        self.is_paused = True
        self.timer.stop()
        self.set_status("status_paused", "warning")

    def resume_analysis(self):
        self.is_paused = False
        interval_ms = self.config.get("interval_minutes", 5) * 60 * 1000
        self.timer.start(interval_ms)
        self.capture_and_send()

    def start_background_process(self):
        self.is_paused = False
        interval_ms = self.config.get("interval_minutes", 5) * 60 * 1000
        self.timer.start(interval_ms)
        self.capture_and_send()
        self.tray_icon.showMessage(
            "AuraTwin", self.t("tray_started"), QSystemTrayIcon.Information, 2000
        )

    def capture_and_send(self):
        if self._capture_worker is not None and self._capture_worker.isRunning():
            return
        self._capture_worker = CaptureWorker(
            self.config.get("app_key"), AWS_API_URL
        )
        self._capture_worker.status_update.connect(self.set_status)
        self._capture_worker.start()


# --- BAŞLAT ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)

    window = AuraTwinApp()
    window.show()
    sys.exit(app.exec_())
