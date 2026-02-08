import random
import string
import math
from PySide6.QtWidgets import QLabel, QProgressBar, QListWidget, QFrame, QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QBrush

# --- 1. SCANLINE OVERLAY ---
class ScanlineOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scroll)
        self.timer.start(30)

    def _scroll(self):
        self.offset = (self.offset + 2) % 4
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0, 40))
        for y in range(self.offset, self.height(), 4):
            painter.drawLine(0, y, self.width(), y)

# --- 2. TERMINAL LOG ---
class TerminalLog(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setStyleSheet("""
            background-color: #0d0d0d; border: 1px solid #333; 
            color: #00ff41; font-family: 'Consolas'; font-size: 10px;
        """)
    def add_entry(self, text, color=None):
        self.addItem(f">> {text}")
        if color: self.item(self.count()-1).setForeground(QBrush(QColor(color)))
        self.scrollToBottom()
        if self.count() > 50: self.takeItem(0)

# --- 3. CYBER HEX STREAM ---
class CyberHexStream(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(300) 
    def _update(self):
        chars = "0123456789ABCDEF"
        cols = max(1, self.width() // 28)
        max_lines = max(1, self.height() // 18)
        self.lines.append(" ".join(["".join(random.choices(chars, k=2)) for _ in range(cols)]))
        while len(self.lines) > max_lines: self.lines.pop(0)
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setFont(QFont("Consolas", 10, QFont.Bold))
        for i, line in enumerate(self.lines):
            alpha = int(255 * ((i + 1) / len(self.lines)))
            painter.setPen(QColor(76, 175, 80, alpha))
            painter.drawText(10, (i + 1) * 18, line)

# --- 4. DECRYPT LABEL ---
class DecryptLabel(QLabel):
    def __init__(self, text="", parent=None, size=18):
        super().__init__(text, parent); self.final_text = text; self.steps = 0
        self.setStyleSheet(f"color: #4caf50; font-weight: bold; font-size: {size}px; font-family: 'Consolas';")
        self.timer = QTimer(self); self.timer.timeout.connect(self._scramble)
    def setText(self, text): self.final_text = text; self.steps = 0; self.timer.start(30)
    def _scramble(self):
        self.steps += 1
        if self.steps > 20: self.timer.stop(); super().setText(self.final_text); return
        chars = string.ascii_uppercase + string.digits + "#%&"
        super().setText("".join(random.choice(chars) if self.final_text[i] != " " and i >= (self.steps // 2) else self.final_text[i] for i in range(len(self.final_text))))

# --- 5. PROGRESS BAR ---
class HackerProgressBar(QProgressBar):
    def __init__(self, parent=None): super().__init__(parent); self.setFixedHeight(35)
    def paintEvent(self, event):
        painter = QPainter(self); rect = self.rect(); painter.setBrush(QColor("#111")); painter.drawRect(rect)
        inner = rect.adjusted(3,3,-3,-3); val = self.value() / (self.maximum() or 100)
        painter.setBrush(QColor("#4caf50")); painter.drawRect(inner.x(), inner.y(), int(inner.width()*val), inner.height())
        painter.setPen(QColor("#fff")); painter.drawText(rect, Qt.AlignCenter, f"{int(val*100)}%")

# --- 6. CYBER GRAPH ---
class CyberGraph(QWidget):
    def __init__(self, parent=None): super().__init__(parent); self.values = [0] * 50
    def update_value(self, v): self.values.append(v); self.values.pop(0); self.update()
    def paintEvent(self, event):
        painter = QPainter(self); w, h = self.width(), self.height()
        path = QPainterPath(); step = w / (len(self.values)-1); path.moveTo(0, h-(self.values[0]/100*h))
        for i, v in enumerate(self.values): path.lineTo(i*step, h-(v/100*h))
        painter.setPen(QPen(QColor(76, 175, 80), 2)); painter.drawPath(path)