import sys
import asyncio
import qasync
import random
import webbrowser
import ctypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QListWidget, QTableWidget, QTableWidgetItem, QProgressBar, 
    QFrame, QHeaderView, QLineEdit, QPushButton, QInputDialog, 
    QStackedWidget, QAbstractItemView, QListWidgetItem, QDialog,
    QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QBrush, QFont, QCursor, QIcon
from core import TelegramWorker
from assets import (DecryptLabel, HackerProgressBar, TerminalLog, CyberGraph, 
                    CyberHexStream, ScanlineOverlay)

# Windows Taskbar Icon Fix
try:
    myappid = u'teleflow.downloader.pro.v3'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

STYLESHEET = """
    QMainWindow { background-color: #121212; }
    QLabel { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
    QLineEdit { 
        background-color: #1e1e1e; border: 1px solid #333; border-radius: 4px;
        color: white; padding: 12px; font-family: 'Consolas', monospace; font-size: 13px;
    }
    QLineEdit:focus { border: 1px solid #4caf50; background-color: #252526; }
    QFrame#Panel { background-color: #1e1e1e; border: 1px solid #333; border-radius: 6px; }
    QFrame#Footer { background-color: #0f0f0f; border-top: 1px solid #333; }
    QFrame#StatBox { background-color: #161616; border: 1px solid #333; border-radius: 4px; }
    
    QLabel#GuideHeader { color: #4caf50; font-weight: bold; font-size: 18px; margin-bottom: 15px; }
    QLabel#GuideStep { color: #aaa; font-size: 13px; line-height: 1.6; }
    
    QListWidget { background-color: #1e1e1e; border: 1px solid #333; border-radius: 6px; color: #ddd; outline: none; }
    QListWidget::item { padding: 12px; border-bottom: 1px solid #252526; }
    QListWidget::item:selected { background-color: #2d362e; border-left: 4px solid #4caf50; color: white; }
    
    QTableWidget { background-color: #121212; border: none; gridline-color: transparent; color: #888; alternate-background-color: #161616; outline: none; selection-background-color: transparent; }
    QTableWidget::indicator { width: 14px; height: 14px; border: 1px solid #ffffff; border-radius: 2px; background-color: transparent; }
    QTableWidget::indicator:checked { background-color: #4caf50; border: 1px solid #ffffff; }
    QTableWidget::item:hover { color: #ffffff; background-color: #1c1c1c; }
    QHeaderView::section { background-color: #121212; color: #555; border: none; border-bottom: 1px solid #333; padding: 10px; font-weight: bold; text-transform: uppercase; font-size: 10px; }

    QPushButton { background-color: #2e7d32; color: white; border: none; padding: 10px 20px; font-weight: 600; border-radius: 4px; }
    QPushButton:hover { background-color: #388e3c; }
    QPushButton#Secondary { background-color: #333; color: #ccc; }
    QPushButton#Destructive { background-color: #b71c1c; color: white; }
    QPushButton#FilterBtn { background-color: #222; color: #888; border: 1px solid #333; }
    QPushButton#FilterBtn:checked { background-color: #2d362e; color: #4caf50; border: 1px solid #4caf50; }
    
    QLabel#StatValueGreen { color: #4caf50; font-size: 16px; font-family: 'Consolas'; font-weight: bold; }
"""

class MainWindow(QMainWindow):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("TELEFLOW v3.0 // PRO"); self.resize(1200, 800); self.setStyleSheet(STYLESHEET)
        
        self.central_container = QWidget(); self.setCentralWidget(self.central_container)
        self.global_layout = QVBoxLayout(self.central_container); self.global_layout.setContentsMargins(0,0,0,0)
        
        self.scanlines = ScanlineOverlay(self.central_container); self.scanlines.raise_()
        self.stack = QStackedWidget(); self.global_layout.addWidget(self.stack)

        self.init_footer(); self.init_login_page(); self.init_chat_page(); self.init_video_page(); self.init_download_page()
        self.is_downloading = False; self.all_chats = []; self.current_videos = []; self.sort_reverse = False
        
        self.worker.saved_creds_found.connect(self.on_creds_found); self.worker.request_creds.connect(lambda: self.stack.setCurrentIndex(0))
        self.worker.login_success.connect(lambda: self.stack.setCurrentIndex(1)); self.worker.chats_loaded.connect(self.store_and_populate_chats)
        self.worker.videos_loaded.connect(self.populate_videos); self.worker.download_started.connect(self.on_dl_start)
        self.worker.download_progress.connect(self.on_dl_progress); self.worker.queue_finished.connect(self.on_queue_finished)
        self.worker.auth_status.connect(self.update_status); self.stack.currentChanged.connect(self.check_footer_visibility)

    def resizeEvent(self, event): self.scanlines.setGeometry(self.rect()); super().resizeEvent(event)

    def init_login_page(self):
        p = QWidget(); layout = QHBoxLayout(p); layout.setContentsMargins(60, 0, 60, 0); layout.setSpacing(0)
        
        # LEFT: SYMMETRIC INSTRUCTIONS
        guide_area = QWidget(); g_main = QVBoxLayout(guide_area); g_main.setAlignment(Qt.AlignCenter)
        guide_pan = QFrame(); guide_pan.setObjectName("Panel"); guide_pan.setFixedWidth(450); g_ly = QVBoxLayout(guide_pan); g_ly.setContentsMargins(40, 40, 40, 40); g_ly.setSpacing(15)
        g_ly.addWidget(QLabel("UPLINK CONFIGURATION", objectName="GuideHeader", alignment=Qt.AlignCenter))
        
        # Fixed 1st Line Alignment
        step1 = QLabel('1. Visit <a href="https://my.telegram.org" style="color: #4caf50; text-decoration: underline;">my.telegram.org</a> in your browser.', objectName="GuideStep")
        step1.setOpenExternalLinks(True); step1.setWordWrap(True); g_ly.addWidget(step1)
        
        instructions = [
            "2. Enter your phone number (e.g., +91...)",
            "3. Submit the 'Login Code' from your Telegram App.",
            "4. Access 'API Development Tools' inside.",
            "5. Register a new App to generate your unique keys.",
            "6. Copy 'App api_id' and 'App api_hash' to the right."
        ]
        for text in instructions:
            lbl = QLabel(text, objectName="GuideStep"); lbl.setWordWrap(True); g_ly.addWidget(lbl)
        g_main.addWidget(guide_pan); layout.addWidget(guide_area, 1)

        # RIGHT: FORM
        login_area = QWidget(); l_main = QVBoxLayout(login_area); l_main.setAlignment(Qt.AlignCenter)
        login_pan = QFrame(); login_pan.setObjectName("Panel"); login_pan.setFixedWidth(450); pl = QVBoxLayout(login_pan); pl.setSpacing(20); pl.setContentsMargins(40,40,40,40)
        self.login_t = DecryptLabel("SYSTEM LOGIN", size=24); self.login_t.setAlignment(Qt.AlignCenter); pl.addWidget(self.login_t)
        self.inp_api = QLineEdit(placeholderText="API ID"); pl.addWidget(self.inp_api)
        self.inp_hash = QLineEdit(placeholderText="API Hash"); pl.addWidget(self.inp_hash)
        self.inp_phone = QLineEdit(placeholderText="Phone Number"); pl.addWidget(self.inp_phone)
        btn = QPushButton("ESTABLISH SECURE UPLINK"); btn.clicked.connect(self.do_connect); pl.addWidget(btn)
        self.lbl_login_status = QLabel("Ready...", alignment=Qt.AlignCenter); pl.addWidget(self.lbl_login_status)
        l_main.addWidget(login_pan); layout.addWidget(login_area, 1); self.stack.addWidget(p)

    def init_chat_page(self):
        p = QWidget(); layout = QVBoxLayout(p); layout.setContentsMargins(50,50,50,50)
        h_ly = QHBoxLayout(); h_ly.addWidget(DecryptLabel("SOURCE NODE SELECTION", size=20)); h_ly.addStretch()
        h_ly.addWidget(QLabel("🟢 Channel | 🔵 Group | 👤 DM", styleSheet="color:#888; font-family:'Consolas'; font-size:11px; font-weight:bold;")); layout.addLayout(h_ly)
        f_bar = QHBoxLayout(); self.search_chats = QLineEdit(placeholderText="Search Nodes..."); self.search_chats.setFixedWidth(250); self.search_chats.textChanged.connect(self.apply_chat_filter); f_bar.addWidget(self.search_chats); f_bar.addSpacing(20)
        self.btn_all = QPushButton("ALL"); self.btn_ch = QPushButton("CHANNELS"); self.btn_gr = QPushButton("GROUPS"); self.btn_dm = QPushButton("DMs")
        for b in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]:
            b.setCheckable(True); b.setObjectName("FilterBtn"); b.setFixedWidth(100); b.clicked.connect(self.apply_chat_filter); f_bar.addWidget(b)
        self.btn_all.setChecked(True); f_bar.addStretch(); layout.addLayout(f_bar)
        self.chat_list = QListWidget(); self.chat_list.itemClicked.connect(lambda i: [self.stack.setCurrentIndex(2), asyncio.create_task(self.worker.scan_chat(i.data(Qt.UserRole)))]); layout.addWidget(self.chat_list); self.stack.addWidget(p)

    def init_video_page(self):
        p = QWidget(); layout = QVBoxLayout(p); layout.setContentsMargins(40,40,40,40); layout.addWidget(DecryptLabel("PAYLOAD DIRECTORY", size=20))
        sl = QHBoxLayout(); self.search_videos = QLineEdit(placeholderText="Search Payloads..."); self.search_videos.setFixedWidth(300); self.search_videos.textChanged.connect(self.refresh_video_table); sl.addWidget(self.search_videos); sl.addSpacing(20); self.btn_sort = QPushButton("[ SORT ]"); self.btn_sort.setObjectName("Secondary"); self.btn_sort.clicked.connect(self.toggle_sort); sl.addWidget(self.btn_sort); sl.addStretch(); layout.addLayout(sl)
        self.video_table = QTableWidget(0, 4); self.video_table.setHorizontalHeaderLabels(["SEL", "NO", "FILENAME", "SIZE"]); self.video_table.setAlternatingRowColors(True); self.video_table.setShowGrid(False); self.video_table.setSelectionBehavior(QAbstractItemView.SelectRows); self.video_table.setSelectionMode(QAbstractItemView.SingleSelection); self.video_table.setEditTriggers(QAbstractItemView.NoEditTriggers); self.video_table.setFocusPolicy(Qt.NoFocus); self.video_table.verticalHeader().setVisible(False)
        self.video_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed); self.video_table.setColumnWidth(0, 45); self.video_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed); self.video_table.setColumnWidth(1, 60); self.video_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch); self.video_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed); self.video_table.setColumnWidth(3, 100); self.video_table.cellDoubleClicked.connect(self.on_video_cell_double_click); layout.addWidget(self.video_table)
        bl = QHBoxLayout(); bk = QPushButton("BACK"); bk.setObjectName("Secondary"); bk.clicked.connect(lambda: self.stack.setCurrentIndex(1)); self.btn_sel_all = QPushButton("SELECT ALL"); self.btn_sel_all.setObjectName("Secondary"); self.btn_sel_all.clicked.connect(self.toggle_select_all); dl = QPushButton("START EXFILTRATION"); dl.clicked.connect(self.start_download_batch); bl.addWidget(bk); bl.addWidget(self.btn_sel_all); bl.addStretch(); bl.addWidget(dl); layout.addLayout(bl); self.stack.addWidget(p)

    def _make_visual_panel(self, widget):
        b = QFrame(); b.setObjectName("Panel"); b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); vl = QVBoxLayout(b); vl.setContentsMargins(0,0,0,0); vl.addWidget(widget); return b

    def init_download_page(self):
        p = QWidget(); layout = QVBoxLayout(p); layout.setContentsMargins(40, 40, 40, 40); h_l = QHBoxLayout(); self.dl_header = DecryptLabel("EXFILTRATION IN PROGRESS", size=20); h_l.addWidget(self.dl_header); h_l.addStretch(); btn_ab = QPushButton("ABORT / BACK"); btn_ab.setObjectName("Destructive"); btn_ab.setFixedSize(120, 30); btn_ab.clicked.connect(self.go_back_keep_downloading); h_l.addWidget(btn_ab); layout.addLayout(h_l)
        dash = QHBoxLayout(); q_p = QFrame(); q_p.setObjectName("Panel"); q_p.setFixedWidth(300); q_lay = QVBoxLayout(q_p); q_lay.addWidget(QLabel(">> QUEUE")); self.queue_list = QListWidget(); self.queue_list.setStyleSheet("border:none;"); q_lay.addWidget(self.queue_list); dash.addWidget(q_p)
        ops_p = QVBoxLayout(); ops_p.setSpacing(15); visuals = QHBoxLayout(); self.term_log = TerminalLog(); self.graph = CyberGraph(); self.hex_stream = CyberHexStream(); visuals.addWidget(self._make_visual_panel(self.term_log), 1); visuals.addWidget(self._make_visual_panel(self.graph), 1); visuals.addWidget(self._make_visual_panel(self.hex_stream), 1); ops_p.addLayout(visuals, 1); self.lbl_current_file = QLabel("Ready..."); self.lbl_current_file.setStyleSheet("font-size:14px; color:#4caf50; font-weight:bold;"); ops_p.addWidget(self.lbl_current_file); ctrl_b = QFrame(); ctrl_b.setObjectName("Panel"); ctrl_l = QVBoxLayout(ctrl_b); ctrl_l.setContentsMargins(15,15,15,15); self.dl_bar = HackerProgressBar(); ctrl_l.addWidget(self.dl_bar); stats_g = QGridLayout(); stats_g.setSpacing(10); stats_g.addWidget(self.create_stat_box("THROUGHPUT", "0.0 MB/s", "lbl_speed"), 0, 0); stats_g.addWidget(self.create_stat_box("TIME_REMAIN", "00:00:00", "lbl_eta"), 0, 1); stats_g.addWidget(self.create_stat_box("PACKET_SIZE", "0 / 0 MB", "lbl_size"), 0, 2); stats_g.addWidget(self.create_stat_box("PKT_LOSS", "0.00%", "lbl_loss", True), 1, 0); stats_g.addWidget(self.create_stat_box("CYPHER", "AES-256", "lbl_enc", True), 1, 1); stats_g.addWidget(self.create_stat_box("DISK_I/O", "ACTIVE", "lbl_disk", True), 1, 2); ctrl_l.addLayout(stats_g); ops_p.addWidget(ctrl_b); btn_l = QHBoxLayout(); btn_bk = QPushButton("BACK"); btn_bk.setObjectName("Secondary"); btn_bk.clicked.connect(self.go_back_keep_downloading); self.btn_pause = QPushButton("QUEUE PAUSE"); self.btn_pause.setObjectName("Amber"); self.btn_pause.clicked.connect(self.toggle_pause); self.btn_st = QPushButton("STOP"); self.btn_st.setObjectName("Destructive"); self.btn_st.clicked.connect(self.stop_download); btn_l.addWidget(btn_bk); btn_l.addWidget(self.btn_pause); btn_l.addWidget(self.btn_st); ops_p.addLayout(btn_l); dash.addLayout(ops_p, 3); layout.addLayout(dash); self.stack.addWidget(p)

    def init_footer(self):
        self.footer = QFrame(); self.footer.setObjectName("Footer"); self.footer.setFixedHeight(75); self.footer.hide(); layout = QHBoxLayout(self.footer); layout.setContentsMargins(20, 10, 20, 10); self.foot_lbl_name = QLabel("..."); self.foot_lbl_name.setStyleSheet("font-weight: bold; color: white;"); layout.addWidget(self.foot_lbl_name, 1); self.foot_lbl_stat = QLabel("0%"); layout.addWidget(self.foot_lbl_stat); self.foot_btn_pause = QPushButton("QUEUE PAUSE"); self.foot_btn_pause.setObjectName("Amber"); self.foot_btn_pause.setFixedSize(135, 35); self.foot_btn_pause.clicked.connect(self.toggle_pause); layout.addWidget(self.foot_btn_pause); btn_st = QPushButton("STOP"); btn_st.setObjectName("Destructive"); btn_st.setFixedSize(80, 35); btn_st.clicked.connect(self.stop_download); layout.addWidget(btn_st); btn_ex = QPushButton("EXPAND"); btn_ex.setFixedSize(100, 35); btn_ex.clicked.connect(lambda: self.stack.setCurrentIndex(3)); layout.addWidget(btn_ex); self.global_layout.addWidget(self.footer)

    def go_back_keep_downloading(self): self.stack.setCurrentIndex(2); self.check_footer_visibility()
    def toggle_pause(self): is_p = (self.btn_pause.text() == "QUEUE PAUSE"); self.btn_pause.setText("QUEUE RESUME" if is_p else "QUEUE PAUSE"); self.foot_btn_pause.setText(self.btn_pause.text()); self.worker.set_pause(is_p); self.term_log.add_entry(f"SYSTEM: {'PAUSE' if is_p else 'RESUME'} SIGNAL RECEIVED", "#ff8f00" if is_p else "#00ff41")
    def stop_download(self): self.worker.stop_task(); self.term_log.add_entry("KILL SIGNAL SENT.", "#b71c1c")
    def on_dl_start(self, f, r): self.is_downloading = True; self.check_footer_visibility(); self.lbl_current_file.setText(f">> EXFIL: {f}"); self.foot_lbl_name.setText(f"EXFIL: {f[:20]}..."); self.dl_bar.setValue(0); self.term_log.clear(); self.queue_list.clear(); [self.queue_list.addItem(n) for n in r]
    def on_dl_progress(self, n, p, s, e, ps): self.dl_bar.setValue(p); self.lbl_speed.setText(s); self.lbl_eta.setText(e); self.lbl_size.setText(ps); self.foot_lbl_stat.setText(f"{p}%"); self.graph.update_value(min(100, int(p)+random.randint(-5,5))); self.lbl_loss.setText(f"0.0{random.randint(1,5)}%"); self.lbl_disk.setText(f"{random.randint(50,200)} MB/s")
    def on_queue_finished(self): self.is_downloading = False; self.check_footer_visibility(); self.lbl_current_file.setText("COMPLETE")
    def check_footer_visibility(self): self.footer.setVisible(self.is_downloading and self.stack.currentIndex() != 3)
    def create_stat_box(self, t, v, o, g=False): b = QFrame(); b.setObjectName("StatBox"); vl = QVBoxLayout(b); vl.addWidget(QLabel(t, objectName="StatTitle")); lb = QLabel(v, objectName="StatValueGreen" if g else "StatValue"); vl.addWidget(lb); setattr(self, o, lb); return b
    def store_and_populate_chats(self, chats): self.all_chats = chats; self.apply_chat_filter(); self.stack.setCurrentIndex(1)
    
    def apply_chat_filter(self):
        s = self.sender(); [b.setChecked(False) for b in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm] if s and s in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]]
        if s and s in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]: s.setChecked(True)
        search_text = self.search_chats.text().lower(); self.chat_list.clear()
        for c in self.all_chats:
            t = c.get('type'); show_type = self.btn_all.isChecked() or (self.btn_ch.isChecked() and t == 'channel') or (self.btn_gr.isChecked() and t == 'group') or (self.btn_dm.isChecked() and t == 'dm')
            if show_type and search_text in c['name'].lower():
                tag = "🟢 " if t == 'channel' else "🔵 " if t == 'group' else "👤 "
                item = QListWidgetItem(f"{tag} {c['name']}"); item.setData(Qt.UserRole, c['id']); self.chat_list.addItem(item)
    
    def populate_videos(self, v): self.current_videos = v; self.refresh_video_table()
    def toggle_sort(self): self.sort_reverse = not self.sort_reverse; self.current_videos.sort(key=lambda x: x['id'], reverse=self.sort_reverse); self.refresh_video_table()
    
    def refresh_video_table(self):
        s_txt = self.search_videos.text().lower(); self.video_table.setRowCount(0); f_vids = [v for v in self.current_videos if s_txt in v['name'].lower()]; self.video_table.setRowCount(len(f_vids))
        for i, v in enumerate(f_vids):
            c = QTableWidgetItem()
            # AUTO-CHECK matches while typing
            is_checked = Qt.Checked if s_txt and s_txt in v['name'].lower() else Qt.Unchecked
            c.setCheckState(is_checked)
            self.video_table.setItem(i,0,c); num = QTableWidgetItem(str(i+1)); num.setTextAlignment(Qt.AlignCenter); self.video_table.setItem(i,1,num); self.video_table.setItem(i,2,QTableWidgetItem(v['name'])); sz = QTableWidgetItem(v['size']); sz.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter); self.video_table.setItem(i,3,sz)

    def on_video_cell_double_click(self, row, col):
        check_item = self.video_table.item(row, 0); check_item.setCheckState(Qt.Checked if check_item.checkState() == Qt.Unchecked else Qt.Unchecked)
    def toggle_select_all(self):
        if not self.video_table.rowCount(): return
        ns = Qt.Checked if self.video_table.item(0,0).checkState() == Qt.Unchecked else Qt.Unchecked
        for i in range(self.video_table.rowCount()): self.video_table.item(i,0).setCheckState(ns)
    def start_download_batch(self):
        q = [self.current_videos[i] for i in range(self.video_table.rowCount()) if self.video_table.item(i,0).checkState() == Qt.Checked]
        if q: self.stack.setCurrentIndex(3); asyncio.create_task(self.worker.start_downloads(q))
    def on_creds_found(self, a, h, p): self.inp_api.setText(a); self.inp_hash.setText(h); self.inp_phone.setText(p)
    def do_connect(self): asyncio.create_task(self.worker.connect_client(self.inp_api.text(), self.inp_hash.text(), self.inp_phone.text()))
    def update_status(self, m): self.lbl_login_status.setText(m)
    def ask_otp(self): c, o = QInputDialog.getText(self, "OTP", "Code:"); [asyncio.create_task(self.worker.submit_otp(c)) if o else None]
    def ask_password(self): p, o = QInputDialog.getText(self, "2FA", "Pwd:", QLineEdit.Password); [asyncio.create_task(self.worker.submit_password(p)) if o else None]

def main():
    app = QApplication(sys.argv); loop = qasync.QEventLoop(app); asyncio.set_event_loop(loop)
    worker = TelegramWorker(); window = MainWindow(worker); window.show(); loop.create_task(worker.check_saved_data())
    with loop: loop.run_forever()

if __name__ == "__main__": main()
