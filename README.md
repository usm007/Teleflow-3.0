## Teleflow v3.0 / GUI

**Secure Telegram Data Exfiltration Suite**

Teleflow is a professional-grade, high-performance Telegram video downloader built with a sleek **Grey & Green** terminal aesthetic. It features a dual-pane authentication system, real-time network telemetry, and a "cyber-ops" inspired interface designed for efficiency and stability.

---

### 🛡️ Key Features

* **Symmetric Security Uplink**: A dual-pane login screen featuring interactive setup instructions and clickable resource links.
* **Encrypted Node Selection**: Filter through your Telegram universe with dedicated categories for **Channels**, **Groups**, and **Direct Messages**.
* **Payload Directory**: A smooth, borderless directory interface with sequential numbering, hover-glow effects, and double-click selection logic.
* **Auto-Select Intelligence**: Integrated search bars that automatically highlight and check files matching your keywords as you type.
* **Real-time Telemetry**: Live throughput graphs, hex data streams, and a terminal log that tracks every packet exfiltrated.
* **Network Resilience**: Comprehensive statistics tracking throughput, packet loss simulation, and disk I/O activity.

---

### 🚀 Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/YOUR_USERNAME/Teleflow.git
cd Teleflow

```


2. **Install Dependencies**
```bash
pip install -r requirements.txt

```


3. **Run the Application**
```bash
python main.py

```



---

### 🛠️ Configuration Guide

To establish a secure uplink, you need your own Telegram API credentials:

1. Navigate to [my.telegram.org](https://my.telegram.org).
2. Login with your phone number and the code sent to your Telegram app.
3. Go to **API Development Tools** and create a new application.
4. Input your generated `api_id` and `api_hash` into the Teleflow login screen.

---

### 🖥️ Tech Stack

* **GUI Framework**: PySide6 (Qt for Python)
* **Telegram Protocol**: Telethon (MTProto)
* **Asynchronous Engine**: qasync (Asyncio integration for Qt)
* **Interface**: Custom CSS-themed widgets with dynamic paint events

---

### 📦 Project Structure

* `main.py`: The central controller managing navigation and high-level UI logic.
* `core.py`: The heavy-duty engine handling Telegram connections and multithreaded downloads.
* `assets.py`: Custom-painted hacker widgets including the graph, hex stream, and scanline overlay.
* `requirements.txt`: Project dependencies for standard environment setup.

---

> **Note**: This tool is intended for personal backup and educational use. Ensure you comply with Telegram's Terms of Service and respect content ownership.