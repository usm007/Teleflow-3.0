import os
import ctypes
import asyncio
import time
from telethon import TelegramClient, errors
from telethon.tl.types import DocumentAttributeVideo, Channel, Chat, User
from PySide6.QtCore import QObject, Signal

# --- CONFIG ---
SESSION_NAME = "video_downloader"
BASE_DIR = os.path.expanduser("~/.tbtgdl")
CRED_FILE = os.path.join(BASE_DIR, "credentials.txt")

class TelegramWorker(QObject):
    auth_status = Signal(str)
    request_creds = Signal()
    saved_creds_found = Signal(str, str, str)
    request_otp = Signal()
    request_password = Signal()
    login_success = Signal()
    session_corrupted = Signal(str)
    chats_loaded = Signal(list)
    videos_loaded = Signal(list)
    download_started = Signal(str, list)
    
    # Global Batch Progress
    download_progress = Signal(str, int, str, str, str) 
    
    # Individual Stats
    individual_progress = Signal(str, int, str, str, str)
    
    queue_finished = Signal()
    operation_aborted = Signal()

    def __init__(self):
        super().__init__()
        self.client = None
        self.phone = None
        self.is_paused = False
        self.is_cancelled = False
        self._current_task = None
        self._batch_total_size = 0
        self._file_progress = {} 

    def set_pause(self, paused: bool):
        self.is_paused = paused

    def stop_task(self):
        self.is_cancelled = True

    async def check_saved_data(self):
        api_id, api_hash, phone = self._load_credentials()
        if api_id and api_hash and phone:
            self.phone = phone
            self.saved_creds_found.emit(api_id, api_hash, phone)
        else:
            self.request_creds.emit()

    async def connect_client(self, api_id, api_hash, phone):
        self._save_credentials(api_id, api_hash, phone)
        self.phone = phone
        try:
            self.client = TelegramClient(SESSION_NAME, int(api_id), api_hash)
            await self.client.connect()
        except Exception as e:
            self.session_corrupted.emit(str(e)); return

        if not await self.client.is_user_authorized():
            try:
                await self.client.send_code_request(self.phone)
                self.request_otp.emit()
            except Exception as e:
                self.auth_status.emit(f"AUTH ERROR: {e}")
        else:
            self.login_success.emit()
            await self.fetch_dialogs()

    async def purge_session(self):
        if self.client: await self.client.disconnect()
        session_path = os.path.join(os.getcwd(), f"{SESSION_NAME}.session")
        if os.path.exists(session_path):
            try: os.remove(session_path)
            except: pass

    async def submit_otp(self, code):
        try:
            await self.client.sign_in(self.phone, code)
            self.login_success.emit()
            await self.fetch_dialogs()
        except errors.SessionPasswordNeededError:
            self.request_password.emit()
        except Exception as e:
            self.auth_status.emit(f"ERROR: {e}")

    async def submit_password(self, password):
        try:
            await self.client.sign_in(password=password)
            self.login_success.emit()
            await self.fetch_dialogs()
        except Exception as e:
            self.auth_status.emit(f"ERROR: {e}")

    async def fetch_dialogs(self):
        dialogs = await self.client.get_dialogs()
        chat_list = []
        for d in dialogs:
            c_type = "dm"
            if isinstance(d.entity, Channel):
                c_type = "channel" if d.entity.broadcast else "group"
            elif isinstance(d.entity, Chat):
                c_type = "group"
            chat_list.append({"id": d.id, "name": d.name, "type": c_type})
        self.chats_loaded.emit(chat_list)

    async def scan_chat(self, chat_id):
        videos = []
        try:
            entity = await self.client.get_entity(chat_id)
            async for msg in self.client.iter_messages(entity, limit=500):
                if msg.media and hasattr(msg.media, 'document'):
                    if any(isinstance(x, DocumentAttributeVideo) for x in msg.media.document.attributes):
                        size_mb = msg.media.document.size / (1024 * 1024)
                        filename = msg.file.name or f"payload_{msg.id}.mp4"
                        videos.append({"id": msg.id, "name": filename, "size": f"{size_mb:.2f} MB", "msg": msg})
            self.videos_loaded.emit(videos)
        except Exception as e:
            self.auth_status.emit(f"SCAN ERROR: {e}")

    # --- MODIFIED: ACCEPT CONCURRENT LIMIT ---
    async def start_downloads(self, download_queue, concurrent_limit=3):
        self._current_task = asyncio.create_task(self._start_downloads_logic(download_queue, concurrent_limit))
        await self._current_task

    async def _start_downloads_logic(self, download_queue, concurrent_limit):
        os.makedirs("Downloads", exist_ok=True)
        self.is_cancelled = False
        self.is_paused = False
        
        # Batch Globals
        self._batch_total_size = sum([item['msg'].file.size for item in download_queue])
        self._file_progress = {item['name']: 0 for item in download_queue}
        self._global_start_time = time.time()
        
        # Dynamic Semaphore
        sem = asyncio.Semaphore(concurrent_limit)
        print(f"[DEBUG] Starting with {concurrent_limit} concurrent threads")
        
        async def download_worker(item):
            filename = item['name']
            file_size = item['msg'].file.size
            path = os.path.join("Downloads", filename)
            ind_start_time = time.time()
            
            async with sem:
                if self.is_cancelled: return
                while self.is_paused:
                    if self.is_cancelled: return
                    await asyncio.sleep(1)

                self.download_started.emit(filename, [])
                ind_start_time = time.time()

                def progress_callback(current, total):
                    if self.is_cancelled: raise Exception("MANUAL_ABORT")
                    
                    # Individual Stats
                    now = time.time()
                    ind_elapsed = now - ind_start_time or 0.001
                    ind_speed = current / ind_elapsed
                    ind_percent = int((current / file_size) * 100)
                    ind_speed_str = f"{ind_speed / (1024*1024):.2f} MB/s"
                    ind_remaining = file_size - current
                    ind_eta = ind_remaining / ind_speed if ind_speed > 0 else 0
                    ind_eta_str = time.strftime('%M:%S', time.gmtime(ind_eta))
                    ind_size_str = f"{current/(1024*1024):.1f}/{total/(1024*1024):.1f} MB"
                    
                    self.individual_progress.emit(filename, ind_percent, ind_speed_str, ind_eta_str, ind_size_str)
                    
                    # Global Stats
                    self._file_progress[filename] = current
                    global_current = sum(self._file_progress.values())
                    glob_elapsed = now - self._global_start_time or 0.001
                    glob_speed = global_current / glob_elapsed
                    glob_speed_str = f"{glob_speed / (1024*1024):.2f} MB/s"
                    glob_percent = int((global_current / self._batch_total_size) * 100)
                    glob_remaining = self._batch_total_size - global_current
                    glob_eta = glob_remaining / glob_speed if glob_speed > 0 else 0
                    glob_eta_str = time.strftime('%H:%M:%S', time.gmtime(glob_eta))
                    glob_prog_str = f"{global_current/(1024*1024):.1f} / {self._batch_total_size/(1024*1024):.1f} MB"
                    
                    self.download_progress.emit(f"BATCH EXFILTRATION", glob_percent, glob_speed_str, glob_eta_str, glob_prog_str)

                try:
                    await self.client.download_media(item['msg'], file=path, progress_callback=progress_callback)
                    self.individual_progress.emit(filename, 100, "DONE", "00:00", f"{file_size/(1024*1024):.1f} MB")
                except Exception as e:
                    if "MANUAL_ABORT" in str(e): raise e
                    print(f"[ERROR] {filename}: {e}")

        tasks = [asyncio.create_task(download_worker(item)) for item in download_queue]
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            if "MANUAL_ABORT" in str(e):
                self.operation_aborted.emit(); return

        self.queue_finished.emit()

    def _load_credentials(self):
        if not os.path.exists(CRED_FILE): return None, None, None
        try:
            with open(CRED_FILE, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines()]
            return (lines[0], lines[1], lines[2]) if len(lines) >= 3 else (None, None, None)
        except: return None, None, None

    def _save_credentials(self, api_id, api_hash, phone):
        os.makedirs(BASE_DIR, exist_ok=True)
        try:
            if os.name == "nt" and os.path.exists(CRED_FILE): ctypes.windll.kernel32.SetFileAttributesW(CRED_FILE, 0x80)
        except: pass
        with open(CRED_FILE, "w", encoding="utf-8") as f: f.write(f"{api_id}\n{api_hash}\n{phone}")
        try:
            if os.name == "nt": ctypes.windll.kernel32.SetFileAttributesW(CRED_FILE, 0x02)
        except: pass
