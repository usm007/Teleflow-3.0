import random
import string
import math
from PySide6.QtWidgets import QLabel, QProgressBar, QListWidget, QFrame, QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QRect
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

# --- 7. MATRIX LOADER (CLI STACK + PROGRESS BAR) ---
class MatrixLoader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(50)
        
        self.found_count = 0
        self.progress_val = 0
        self.log_lines = []
        
        # Fake Data for CLI Side Panel
        self.modules = [
            ("NET_HOOK", "ACTIVE"),
            ("BYPASS_V4", "OK"),
            ("PACKET_SNIFF", "RUNNING"),
            ("ROOT_ACCESS", "GRANTED"),
            ("DB_INJECT", "PENDING"),
            ("PROXY_CHAIN", "ROTATING")
        ]
        
        self.target_info = [
            "TARGET: TELEGRAM_API",
            f"PORT: 443 [OPEN]",
            "AUTH: BEARER_TOKEN",
            "CIPHER: AES-256-GCM"
        ]

    def set_count(self, c):
        self.found_count = c

    def _update(self):
        # 1. Animate Progress Bar (Looping 0-100% to show activity)
        self.progress_val += 1
        if self.progress_val > 100: self.progress_val = 0
        
        # 2. Update Fake Logs (Rolling Hex Dump)
        if random.random() > 0.7:
            cmds = ["MOV", "XOR", "JMP", "PUSH", "POP", "CALL", "RET"]
            addr = "".join(random.choices("0123456789ABCDEF", k=4))
            val  = "".join(random.choices("0123456789ABCDEF", k=2))
            cmd  = random.choice(cmds)
            self.log_lines.append(f"0x{addr} : {cmd} {val}")
            if len(self.log_lines) > 12: self.log_lines.pop(0)
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(10, 10, 10)) # Dark Background
        
        w, h = self.width(), self.height()
        left_panel_w = 250
        
        # --- LEFT PANEL: CLI STACK ---
        # Darker background for sidebar
        painter.fillRect(0, 0, left_panel_w, h, QColor(15, 15, 15))
        # Divider Line
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.drawLine(left_panel_w, 0, left_panel_w, h)
        
        painter.setFont(QFont("Consolas", 10))
        x_padding = 15
        current_y = 25
        
        # Section 1: Target Info
        painter.setPen(QColor(0, 255, 65))
        painter.drawText(x_padding, current_y, ">> TARGET_INFO")
        current_y += 20
        painter.setPen(QColor(180, 255, 180))
        for line in self.target_info:
            painter.drawText(x_padding + 5, current_y, line)
            current_y += 18
            
        current_y += 20
        
        # Section 2: Modules
        painter.setPen(QColor(0, 255, 65))
        painter.drawText(x_padding, current_y, ">> ACTIVE_MODULES")
        current_y += 20
        for name, status in self.modules:
            color = QColor(100, 255, 100)
            if status == "PENDING": color = QColor(255, 200, 50)
            # Random glitch effect
            if random.random() > 0.98: color = QColor(255, 255, 255) 
            
            painter.setPen(color)
            painter.drawText(x_padding + 5, current_y, f"[{name:<12}] {status}")
            current_y += 18
            
        current_y += 20
        
        # Section 3: Rolling Log (Fills remaining height)
        painter.setPen(QColor(0, 255, 65))
        painter.drawText(x_padding, current_y, ">> MEMORY_STREAM")
        current_y += 20
        painter.setPen(QColor(100, 200, 100))
        for line in self.log_lines:
            painter.drawText(x_padding + 5, current_y, line)
            current_y += 18

        # --- RIGHT PANEL: HUD & PROGRESS ---
        center_x = left_panel_w + (w - left_panel_w) // 2
        center_y = h // 2
        
        # 1. Main Title
        painter.setFont(QFont("Consolas", 24, QFont.Bold))
        painter.setPen(QColor(0, 255, 65))
        title = "SYSTEM INFILTRATION"
        tm = painter.fontMetrics()
        painter.drawText(center_x - tm.horizontalAdvance(title)//2, center_y - 80, title)
        
        # 2. Subtitle
        painter.setFont(QFont("Consolas", 12))
        painter.setPen(QColor(200, 255, 200))
        sub = "SCANNING SECTOR 7G..."
        sm = painter.fontMetrics()
        painter.drawText(center_x - sm.horizontalAdvance(sub)//2, center_y - 45, sub)
        
        # 3. BIG PROGRESS BAR
        bar_w = 400
        bar_h = 35
        bar_x = center_x - bar_w // 2
        bar_y = center_y - 10
        
        # Frame
        painter.setPen(QPen(QColor(0, 255, 65), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(bar_x, bar_y, bar_w, bar_h)
        
        # Fill (Segmented Blocks)
        painter.setBrush(QColor(0, 255, 65))
        painter.setPen(Qt.NoPen)
        
        fill_pct = self.progress_val / 100
        fill_width = int(bar_w * fill_pct)
        
        block_w = 12
        spacing = 3
        for bx in range(bar_x + 4, bar_x + fill_width - 4, block_w + spacing):
            if bx + block_w > bar_x + bar_w - 4: break
            painter.drawRect(bx, bar_y + 4, block_w, bar_h - 8)
            
        # Percentage Text
        painter.setFont(QFont("Consolas", 14, QFont.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(bar_x + bar_w + 15, bar_y + 22, f"{self.progress_val}%")

        # 4. Payload Counter
        painter.setFont(QFont("Consolas", 20, QFont.Bold))
        painter.setPen(QColor(255, 255, 0)) # Yellow High-Vis
        count_str = f"PAYLOADS IDENTIFIED: {self.found_count}"
        cm = painter.fontMetrics()
        painter.drawText(center_x - cm.horizontalAdvance(count_str)//2, bar_y + 90, count_str)
