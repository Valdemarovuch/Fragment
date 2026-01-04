# FRAGMENT v1.0.4 // Digital Decay Engine

![Version](https://img.shields.io/badge/version-2.0.0-orange?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge) ![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge) ![Status](https://img.shields.io/badge/Status-Active-red?style=for-the-badge)

**Fragment** is a specialized anti-forensics tool designed to generate high-entropy file decoys. Unlike standard file wipers, Fragment creates a "dead clone" of the target file—preserving metadata and headers while replacing the payload with cryptographically secure noise.

> **Warning:** This tool is intended for educational purposes and security testing (Red Teaming / Honeypot creation). The author is not responsible for data loss due to misuse.

---

## ⚡ Key Features

### 1. Non-Destructive Source
Fragment never touches the original file. It operates on a **read-size-only** basis, ensuring the source data remains physically intact while a corrupted clone is generated.

### 2. Smart Corruption (MIME-Type Injection)
Instead of filling the file with zeros or random noise from the first byte, Fragment employs a **Header Retention Strategy**:
* **First 128 Bytes:** Copied from the original to preserve file signatures (Magic Bytes).
* **Result:** The OS (Windows/Linux) recognizes the file type (e.g., DOCX icon appears correctly), but opening it triggers a "File Corrupted" error instead of an "Unknown Format" error. This is crucial for social engineering and honeypots.

### 3. Timestomping (Forensic Cleaning)
The generated decoy inherits the exact **Access (atime)** and **Modification (mtime)** timestamps of the original file, making the clone indistinguishable from the original in a file explorer list.

### 4. Entropy Injection
The payload is replaced using `os.urandom`, generating cryptographically strong pseudo-random data. This makes the file content mathematically unrecoverable and indistinguishable from encrypted data.

### 5. Cyberpunk UI
Built with **PyWebView** and **TailwindCSS**, offering a modern, hardware-accelerated dark interface with terminal-style logging.

---

## 🛠 Tech Stack

* **Backend:** Python 3.x (File I/O, `os`, `shutil`)
* **Frontend:** HTML5, JavaScript, TailwindCSS (CDN)
* **Bridge:** `pywebview` (Lightweight webview wrapper)

---

## 🚀 Installation & Usage

### Prerequisites
You need Python installed on your system.

```bash
# 1. Install dependencies
pip install pywebview
