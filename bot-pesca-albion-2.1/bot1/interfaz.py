import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor

class BotWindow(QWidget):
    logSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.offset = None
        self.bot_thread = None
        self.bot_running = False
        self.pause_event = threading.Event()
        self.logSignal.connect(self.append_log)

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(450, 450)  # Aumenté el alto de la ventana a 450
        self.setWindowTitle("WATCHMAN BOT DE PESCA 1.3V")

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#121212"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout()

        # --- Barra superior con botón de cierre ---
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(0)

        self.close_button = QPushButton("✖")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #8B0000;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #B22222;
            }
        """)
        self.close_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_button.clicked.connect(self.close)

        top_bar.addStretch()
        top_bar.addWidget(self.close_button)
        layout.addLayout(top_bar)

        # --- Título ---
        self.title = QLabel("🎣 WATCHMAN BOT DE PESCA v1.3", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 10, QFont.Bold))

        # --- Botones ---
        self.btn_start = QPushButton("Iniciar", self)
        self.btn_start.setStyleSheet("background-color: #1DB954; color: white; font-size: 16px; padding: 10px; border-radius: 10px;")
        self.btn_start.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_start.clicked.connect(self.startBot)

        self.btn_pause = QPushButton("Pausar", self)
        self.btn_pause.setStyleSheet("background-color: #FFA500; color: white; font-size: 16px; padding: 10px; border-radius: 10px;")
        self.btn_pause.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_pause.clicked.connect(self.togglePause)
        self.btn_pause.setEnabled(False)

        self.btn_stop = QPushButton("Parar", self)
        self.btn_stop.setStyleSheet("background-color: #E53935; color: white; font-size: 16px; padding: 10px; border-radius: 10px;")
        self.btn_stop.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_stop.clicked.connect(self.stopBot)
        self.btn_stop.setEnabled(False)

        self.status = QLabel("Estado: Inactivo", self)
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 10))

        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 10pt;")
        self.log_area.setFixedHeight(150)  # Ajuste para que el área de logs sea más alta

        # --- Agregar widgets al layout principal ---
        layout.addWidget(self.title)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.status)
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.show()

    def append_log(self, message):
        self.log_area.append(message)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def startBot(self):
        if self.bot_running:
            self.append_log("⚠️ El bot ya está en ejecución.")
            return

        self.status.setText("Estado: Preparando...")
        self.append_log("🕐 Tenés 5 segundos para abrir la ventana de Albion...")
        QTimer.singleShot(5000, self.launchBot)
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.pause_event.clear()

    def launchBot(self):
        self.bot_running = True
        self.status.setText("Estado: Bot activo")
        self.append_log("✅ Bot iniciado.")
        self.bot_thread = threading.Thread(target=self.run_script, daemon=True)
        self.bot_thread.start()

    def run_script(self):
        try:
            from main import iniciar_desde_interfaz
            iniciar_desde_interfaz(log_callback=self.logSignal.emit, pause_event=self.pause_event)
            self.status.setText("Estado: Bot detenido")
            self.append_log("🛑 Bot detenido.")
        except Exception as e:
            self.status.setText("❌ Error al ejecutar el bot")
            self.append_log(f"🚫 Error: {str(e)}")
        finally:
            self.bot_running = False
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_stop.setEnabled(False)

    def togglePause(self):
        if not self.bot_running:
            return

        if self.pause_event.is_set():
            self.pause_event.clear()
            self.btn_pause.setText("Pausar")
            self.status.setText("Estado: Bot activo")
            self.append_log("▶️ Bot reanudado.")
        else:
            self.pause_event.set()
            self.btn_pause.setText("Reanudar")
            self.status.setText("Estado: Bot pausado")
            self.append_log("⏸️ Bot pausado.")

    def stopBot(self):
        self.status.setText("Estado: Detenido por usuario")
        self.append_log("🛑 Bot detenido por el usuario.")
        sys.exit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.offset = None
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = BotWindow()
    sys.exit(app.exec_())
