import sys
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QTextEdit,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor

from src.state_machine import StateMachine, Estado
from src.bot_runner import ejecutar_bot

_COLORES_ESTADO = {
    Estado.DETENIDO:    '#888888',
    Estado.INICIO:      '#FFA500',
    Estado.MONTANDO:    '#1E90FF',
    Estado.NAVEGANDO:   '#1E90FF',
    Estado.DESMONTANDO: '#1E90FF',
    Estado.PESCANDO:    '#1DB954',
    Estado.COMBATE:     '#E53935',
    Estado.HUYENDO:     '#FF6F00',
    Estado.MUERTO:      '#8B0000',
}


class BotWindow(QWidget):
    logSignal   = pyqtSignal(str)
    estadoSignal = pyqtSignal(str, str)  # (nombre, color_hex)

    def __init__(self):
        super().__init__()
        self._sm = None
        self._bot_thread = None
        self._pause_event = threading.Event()
        self._stop_event  = threading.Event()
        self._corriendo = False
        self._initUI()
        self.logSignal.connect(self._append_log)
        self.estadoSignal.connect(self._actualizar_estado_label)

    def _initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(480, 520)
        self.setWindowTitle("WATCHMAN BOT v3.0")

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#121212"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout()

        # Barra superior
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        btn_close = QPushButton("✖")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet(
            "QPushButton { background:#8B0000; color:white; font-weight:bold; border:none; }"
            "QPushButton:hover { background:#B22222; }"
        )
        btn_close.setCursor(QCursor(Qt.PointingHandCursor))
        btn_close.clicked.connect(self.close)
        top_bar.addStretch()
        top_bar.addWidget(btn_close)
        layout.addLayout(top_bar)

        # Titulo
        titulo = QLabel("WATCHMAN BOT v3.0 — Albion Fishing IA")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 9, QFont.Bold))
        titulo.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(titulo)

        # Label de estado
        self._estado_label = QLabel("DETENIDO")
        self._estado_label.setAlignment(Qt.AlignCenter)
        self._estado_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self._estado_label.setStyleSheet(f"color: {_COLORES_ESTADO[Estado.DETENIDO]};")
        layout.addWidget(self._estado_label)

        # Botones
        self._btn_start = self._boton("Iniciar", "#1DB954", self._iniciar)
        self._btn_pause = self._boton("Pausar",  "#FFA500", self._pausar, habilitado=False)
        self._btn_stop  = self._boton("Parar",   "#E53935", self._parar,  habilitado=False)
        layout.addWidget(self._btn_start)
        layout.addWidget(self._btn_pause)
        layout.addWidget(self._btn_stop)

        # Log
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setStyleSheet(
            "background:#1e1e1e; color:#00ff00; font-family:Consolas; font-size:10pt;"
        )
        layout.addWidget(self._log)

        self.setLayout(layout)

    def _boton(self, texto, color, slot, habilitado=True) -> QPushButton:
        btn = QPushButton(texto)
        btn.setStyleSheet(
            f"QPushButton {{ background:{color}; color:white; font-size:15px;"
            f" padding:10px; border-radius:8px; }}"
            f"QPushButton:disabled {{ background:#333; color:#666; }}"
        )
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.clicked.connect(slot)
        btn.setEnabled(habilitado)
        return btn

    def _append_log(self, msg: str):
        self._log.append(msg)
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())

    def _actualizar_estado_label(self, nombre: str, color: str):
        self._estado_label.setText(nombre)
        self._estado_label.setStyleSheet(f"color: {color};")

    def _log_callback(self, msg: str):
        self.logSignal.emit(msg)

    def _estado_callback_wrapper(self):
        """Wrapper que emite senales de estado periodicamente."""
        if self._sm:
            estado = self._sm.estado
            color  = _COLORES_ESTADO.get(estado, '#ffffff')
            self.estadoSignal.emit(estado.name, color)

    def _iniciar(self):
        if self._corriendo:
            return
        self._stop_event.clear()
        self._pause_event.clear()
        self._sm = StateMachine(log_callback=self._log_callback)
        self._corriendo = True

        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self._btn_stop.setEnabled(True)

        self._log.append("Tenés 5 segundos para ir a Albion Online...")

        self._bot_thread = threading.Thread(
            target=self._run_bot, daemon=True
        )
        self._bot_thread.start()

        # Timer que actualiza el label de estado cada 500ms
        self._timer = QTimer()
        self._timer.timeout.connect(self._estado_callback_wrapper)
        self._timer.start(500)

    def _run_bot(self):
        try:
            ejecutar_bot(self._sm, self._pause_event, self._stop_event)
        except Exception as e:
            self.logSignal.emit(f"Error: {e}")
        finally:
            self._corriendo = False
            self._btn_start.setEnabled(True)
            self._btn_pause.setEnabled(False)
            self._btn_stop.setEnabled(False)
            if hasattr(self, '_timer'):
                self._timer.stop()
            self.estadoSignal.emit("DETENIDO", _COLORES_ESTADO[Estado.DETENIDO])

    def _pausar(self):
        if not self._corriendo:
            return
        if self._pause_event.is_set():
            self._pause_event.clear()
            self._btn_pause.setText("Pausar")
        else:
            self._pause_event.set()
            self._btn_pause.setText("Reanudar")

    def _parar(self):
        self._stop_event.set()
        self._pause_event.clear()
        self._log.append("Deteniendo bot...")

    # Soporte para mover la ventana sin barra de titulo
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._offset = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_offset'):
            self.move(event.globalPos() - self._offset)

    def mouseReleaseEvent(self, event):
        self._offset = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = BotWindow()
    ventana.show()
    sys.exit(app.exec_())
