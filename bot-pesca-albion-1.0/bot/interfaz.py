import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor

class BotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.offset = None
        self.bot_thread = None
        self.bot_running = False

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(450, 200)
        self.setWindowTitle("WATCHMAN BOT DE PESCA 1.0V")

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#121212"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout()

        self.title = QLabel("🎣 WATCHMAN BOT DE PESCA 1.0V", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 10, QFont.Bold))

        self.btn_start = QPushButton("Iniciar", self)
        self.btn_start.setStyleSheet(
            "background-color: #1DB954; color: white; font-size: 16px; padding: 10px; border-radius: 10px;"
        )
        self.btn_start.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_start.clicked.connect(self.startBot)

        self.btn_stop = QPushButton("Parar", self)
        self.btn_stop.setStyleSheet(
            "background-color: #E53935; color: white; font-size: 16px; padding: 10px; border-radius: 10px;"
        )
        self.btn_stop.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_stop.clicked.connect(self.stopBot)

        self.status = QLabel("Estado: Inactivo", self)
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 10))

        layout.addWidget(self.title)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.status)

        self.setLayout(layout)
        self.show()

    def startBot(self):
        if self.bot_running:
            return
        self.status.setText("Tenés 10 segundos para abrir Albion...")
        QTimer.singleShot(15000, self.launchBot)

    def launchBot(self):
        self.bot_running = True
        self.status.setText("Estado: Bot activo")
        self.bot_thread = threading.Thread(target=self.run_script, daemon=True)
        self.bot_thread.start()

    def run_script(self):
        try:
            from main import iniciar_desde_interfaz
            iniciar_desde_interfaz()
            self.bot_running = False
            self.status.setText("Estado: Bot detenido")
        except Exception as e:
            self.status.setText("Error al ejecutar el bot")
            print("Error:", e)

    def stopBot(self):
        self.status.setText("Estado: Detenido")
        sys.exit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = BotWindow()
    sys.exit(app.exec_())
