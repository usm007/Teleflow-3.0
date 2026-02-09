```markdown
# TELEFLOW v3.0 - SECURE DATA EXFILTRATION SUITE

**Teleflow** is a professional-grade, high-performance Telegram video downloader built with a sleek **Grey & Green** terminal aesthetic. It features a robust asynchronous engine, a "cyber-ops" inspired interface, and a new **Concurrent Batch Processor** designed for maximum efficiency and stability.

---

## 🛡️ Key Features

### **Core Engine & Performance**
* **Concurrent Downloading:** Download up to **10 files simultaneously**. Includes a dynamic thread selector to balance speed and stability.
* **Robust Network Handler:** Automatically handles **Telegram Data Center (DC) migrations**, preventing downloads from freezing or crashing due to server-side shifts.
* **Session Persistence:** Maintains secure session states to avoid repeated logins.
* **Resumable Queue:** Pause and Resume the entire download batch instantly without losing progress.

### **Cyber-Ops Interface**
* **Symmetric Security Uplink:** A dual-pane login screen featuring interactive setup instructions and clickable resource links.
* **Active Uplink Manifest:** A unified, scrollable dashboard tracking live downloads ("Active") versus pending files ("Queued") with color-coded status indicators.
* **Real-time Telemetry:** A split-view dashboard featuring live throughput graphs, hex data streams, and a "drama" terminal log that tracks every packet exfiltrated.
* **Payload Directory:** A smooth, borderless file manager with "New > Old" and "Old > New" sorting, search highlighting, and one-click selection.

---

## 🚀 Installation & Setup

### **1. Clone the Repository**
```bash
git clone [https://github.com/YOUR_USERNAME/Teleflow.git](https://github.com/YOUR_USERNAME/Teleflow.git)
cd Teleflow

```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt

```

### **3. Run the Application**

```bash
python main.py

```

---

## 📦 Compilation (Build .exe)

To compile Teleflow into a standalone executable that runs without Python installed:

1. **Install PyInstaller:**
```bash
pip install pyinstaller

```


2. **Run the Build Command:**
*(This command ensures the icon is embedded correctly)*
```bash
pyinstaller --noconsole --onefile --name="Teleflow_v3" --icon="icon.ico" --add-data="icon.ico;." main.py

```


3. **Locate App:** Find `Teleflow_v3.exe` in the `dist/` folder.

---

## 🛠️ Configuration Guide

To establish a secure uplink, you need your own Telegram API credentials:

1. Navigate to [my.telegram.org](https://my.telegram.org).
2. Login with your phone number and the code sent to your Telegram app.
3. Go to **API Development Tools** and create a new application.
4. Input your generated `api_id` and `api_hash` into the Teleflow login screen.

---

## 🖥️ Tech Stack

* **GUI Framework:** PySide6 (Qt for Python)
* **Telegram Protocol:** Telethon (MTProto)
* **Asynchronous Engine:** qasync (Asyncio integration for Qt) - *Fixes UI freezing during heavy loads.*
* **Interface:** Custom CSS-themed widgets with dynamic paint events.

---

## 📦 Project Structure

* `main.py`: The central controller managing navigation, the new Split-View UI, and high-level logic.
* `core.py`: The heavy-duty engine handling Telegram connections, concurrent semaphores, and download logic.
* `assets.py`: Custom-painted hacker widgets including the graph, hex stream, and scanline overlay.
* `requirements.txt`: Project dependencies.

---

> **Note:** This tool is intended for personal backup and educational use. Ensure you comply with Telegram's Terms of Service and respect content ownership.

```

```
