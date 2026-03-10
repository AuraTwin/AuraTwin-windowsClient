import sys
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
                             QCheckBox, QSpinBox, QDialog, QMessageBox,
                             QSystemTrayIcon, QMenu, QAction, QFrame)
from PyQt5.QtGui import QIcon, QFont, QPixmap
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
CONFIG_FILE   = "config.json"
LOGO_FILENAME = os.path.join(BASE_DIR, "AuraTwin_Logo.png")

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
        "settings_btn":    "⚙️  Ayarlar",
        "dashboard_btn":   "Dashboard'a Git",
        "minimize_btn":    "Sistem Tepsisine Küçült",
        "logout_btn":      "Çıkış Yap",
        # Durum mesajları
        "status_waiting":    "Bekleniyor...",
        "status_connecting": "Firebase'e bağlanılıyor...",
        "status_active":     "● Aktif — Analiz çalışıyor",
        "status_paused":     "⏸ Analiz duraklatıldı",
        "status_no_camera":  "● Kamera bulunamadı / meşgul",
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
        "settings_heading":  "⚙️  Ayarlar",
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
        "settings_btn":    "⚙️  Settings",
        "dashboard_btn":   "Go to Dashboard",
        "minimize_btn":    "Minimize to Tray",
        "logout_btn":      "Log Out",
        # Status messages
        "status_waiting":    "Waiting...",
        "status_connecting": "Connecting to Firebase...",
        "status_active":     "● Active — Analysis running",
        "status_paused":     "⏸ Analysis paused",
        "status_no_camera":  "● Camera not found / busy",
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
        "settings_heading":  "⚙️  Settings",
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
        self.lbl_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #4C1D95;")
        layout.addWidget(self.lbl_title)

        self._sep(layout)

        # Analiz Aralığı
        self.lbl_interval = QLabel()
        self.lbl_interval.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_interval.setStyleSheet("color: #374151;")
        layout.addWidget(self.lbl_interval)

        row = QHBoxLayout()
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(1, 60)
        self.spin_interval.setValue(self.main.config.get("interval_minutes", 5))
        self.spin_interval.setFixedHeight(40)
        self.spin_interval.setFont(QFont("Segoe UI", 11))
        self.spin_interval.setStyleSheet("""
            QSpinBox {
                border: 2px solid #DDD6FE; border-radius: 10px;
                padding: 0 10px; color: #1E1B4B; background: #FAFAFA;
            }
            QSpinBox:focus { border-color: #7C3AED; }
            QSpinBox::up-button, QSpinBox::down-button { width: 24px; border-radius: 6px; }
        """)
        row.addWidget(self.spin_interval)
        row.addStretch()
        layout.addLayout(row)

        self.lbl_note = QLabel()
        self.lbl_note.setFont(QFont("Segoe UI", 9))
        self.lbl_note.setStyleSheet(
            "color: #6B7280; background-color: #F5F3FF; border-radius: 8px; padding: 10px;"
        )
        self.lbl_note.setWordWrap(True)
        layout.addWidget(self.lbl_note)

        self._sep(layout)

        # Analiz Durumu
        self.lbl_analysis = QLabel()
        self.lbl_analysis.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_analysis.setStyleSheet("color: #374151;")
        layout.addWidget(self.lbl_analysis)

        self.btn_toggle = QPushButton()
        self.btn_toggle.setFixedHeight(44)
        self.btn_toggle.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_analysis)
        layout.addWidget(self.btn_toggle)

        self._sep(layout)

        # Dil Seçimi
        self.lbl_lang = QLabel()
        self.lbl_lang.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_lang.setStyleSheet("color: #374151;")
        layout.addWidget(self.lbl_lang)

        lang_row = QHBoxLayout()
        self.btn_lang_tr = QPushButton("🇹🇷  Türkçe")
        self.btn_lang_en = QPushButton("🇬🇧  English")
        for btn in (self.btn_lang_tr, self.btn_lang_en):
            btn.setFixedHeight(38)
            btn.setFont(QFont("Segoe UI", 10))
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
        self.btn_save.setFont(QFont("Segoe UI", 11, QFont.Bold))
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
        self.spin_interval.setSuffix(t("interval_suffix"))
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
        minutes = self.spin_interval.value()
        self.main.config["interval_minutes"] = minutes
        self.main.save_config()
        if not self.main.is_paused:
            self.main.timer.start(minutes * 60 * 1000)
        self.accept()


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
        # Durum ekranı
        self.btn_settings.setText(self.t("settings_btn"))
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
        self.btn_lang_tr.setStyleSheet(active if self.lang == "tr" else inactive)
        self.btn_lang_en.setStyleSheet(active if self.lang == "en" else inactive)

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
        lbl_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_title.setStyleSheet("color: #4C1D95;")
        cl.addWidget(lbl_title)

        # Alt başlık + Dil Butonu (aynı satırda)
        sub_row = QHBoxLayout()
        lbl_sub = QLabel(self.t("subtitle"))
        lbl_sub.setFont(QFont("Segoe UI", 10))
        lbl_sub.setStyleSheet("color: #7C3AED;")
        sub_row.addWidget(lbl_sub)
        sub_row.addStretch()

        self.btn_lang_tr = QPushButton("TR")
        self.btn_lang_en = QPushButton("EN")
        for btn in (self.btn_lang_tr, self.btn_lang_en):
            btn.setFixedSize(44, 28)
            btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
        self.btn_lang_tr.clicked.connect(lambda: self.apply_language("tr"))
        self.btn_lang_en.clicked.connect(lambda: self.apply_language("en"))
        sub_row.addWidget(self.btn_lang_tr)
        sub_row.addWidget(self.btn_lang_en)
        cl.addLayout(sub_row)

        self._update_login_lang_btns()

        # Ayırıcı
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #EDE9FE;")
        cl.addWidget(line)

        # --- GİRİŞ EKRANI ---
        self.lbl_prompt = QLabel(self.t("prompt"))
        self.lbl_prompt.setAlignment(Qt.AlignCenter)
        self.lbl_prompt.setFont(QFont("Segoe UI", 10))
        self.lbl_prompt.setStyleSheet("color: #374151; margin-top: 4px;")
        cl.addWidget(self.lbl_prompt)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText(self.t("placeholder"))
        self.token_input.setFixedHeight(42)
        self.token_input.setFont(QFont("Segoe UI", 11))
        self.token_input.setAlignment(Qt.AlignCenter)
        self.token_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #DDD6FE; border-radius: 10px;
                padding: 0 12px; color: #1E1B4B; background: #FAFAFA;
            }
            QLineEdit:focus { border: 2px solid #7C3AED; background: #FFFFFF; }
        """)
        if self.config.get("app_key"):
            self.token_input.setText(self.config["app_key"])
        self.token_input.returnPressed.connect(self.on_save_clicked)
        cl.addWidget(self.token_input)

        self.chk_remember = QCheckBox(self.t("remember"))
        self.chk_remember.setFont(QFont("Segoe UI", 9))
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
        self.btn_save.setFont(QFont("Segoe UI", 11, QFont.Bold))
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
        self.btn_register.setFont(QFont("Segoe UI", 10))
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
        self.lbl_welcome.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.lbl_welcome.setStyleSheet("color: #4C1D95;")
        self.lbl_welcome.setWordWrap(True)
        self.lbl_welcome.hide()
        cl.addWidget(self.lbl_welcome)

        self.btn_settings = QPushButton(self.t("settings_btn"))
        self.btn_settings.setFixedHeight(40)
        self.btn_settings.setFont(QFont("Segoe UI", 10))
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

        self.btn_dashboard = QPushButton(self.t("dashboard_btn"))
        self.btn_dashboard.setFixedHeight(44)
        self.btn_dashboard.setFont(QFont("Segoe UI", 10, QFont.Bold))
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
        self.btn_minimize.setFont(QFont("Segoe UI", 10, QFont.Bold))
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
        self.btn_logout.setFont(QFont("Segoe UI", 10))
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
        self.lbl_status.setFont(QFont("Segoe UI", 9))
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
        self.token_input.hide()
        self.chk_remember.hide()
        self.btn_save.hide()
        self.btn_register.hide()
        self.btn_lang_tr.hide()
        self.btn_lang_en.hide()

        self.lbl_welcome.setText(self.t("welcome").format(name=full_name))
        self.lbl_welcome.show()
        self.btn_settings.show()
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
        self.btn_settings.hide()
        self.btn_dashboard.hide()
        self.btn_minimize.hide()
        self.btn_logout.hide()

        self.token_input.clear()
        self.chk_remember.setChecked(False)
        self.lbl_prompt.show()
        self.token_input.show()
        self.chk_remember.show()
        self.btn_save.show()
        self.btn_register.show()
        self.btn_lang_tr.show()
        self.btn_lang_en.show()

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
            QMessageBox.warning(self, "AuraTwin", self.t("err_no_key"))
            return

        self.btn_save.setEnabled(False)
        self.btn_save.setText(self.t("verifying_btn"))
        self.set_status("status_connecting", "info")
        QApplication.processEvents()

        result = validate_app_key(app_key)

        self.btn_save.setEnabled(True)
        self.btn_save.setText(self.t("login_btn"))

        if result == "connection_error":
            self.set_status("status_conn_err", "error")
            QMessageBox.critical(self, self.t("err_conn_title"), self.t("err_conn_msg"))
            return

        if result == "permission_error":
            self.set_status("status_perm_err", "error")
            QMessageBox.critical(self, self.t("err_perm_title"), self.t("err_perm_msg"))
            return

        if result is None:
            self.set_status("status_invalid", "error")
            QMessageBox.warning(self, self.t("err_invalid_title"), self.t("err_invalid_msg"))
            return

        self.config = {
            "app_key":     app_key,
            "uid":         result["uid"],
            "name":        result["name"],
            "surname":     result["surname"],
            "remember_me": self.chk_remember.isChecked(),
            "lang":        self.lang,
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
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Kamera açılamadı.")
            self.set_status("status_no_camera", "error")
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Görüntü alınamadı.")
            self.set_status("status_no_frame", "error")
            return

        # Kamera meşgul kontrolü: ortalama parlaklık 5'in altındaysa siyah frame → kamera başka uygulama tarafından tutuluyor
        if frame.mean() < 5:
            print("Kamera meşgul (siyah frame) — bu periyot pas geçildi.")
            self.set_status("status_no_camera", "warning")
            return

        _, buffer = cv2.imencode('.jpg', frame)
        jpg_b64 = base64.b64encode(buffer).decode('utf-8')

        print(f"Görüntü yakalandı! Boyut: {len(jpg_b64)} karakter.")
        self.set_status("status_active", "success")

        try:
            payload = {
                "app_key":   self.config.get("app_key"),
                "image":     jpg_b64,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            response = requests.post(AWS_API_URL, json=payload, timeout=15)
            print(f"AWS yanıtı: {response.status_code} — {response.text[:200]}")
            if response.status_code == 200:
                self.set_status("status_active", "success")
            else:
                self.set_status("status_conn_err", "error")
        except requests.RequestException as e:
            print(f"AWS bağlantı hatası: {e}")
            self.set_status("status_conn_err", "error")


# --- BAŞLAT ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)

    window = AuraTwinApp()
    window.show()
    sys.exit(app.exec_())
