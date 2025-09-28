# 🎮 MINECRAFT HAND CONTROLLER - ORUCEXE


A **hand gesture controller** for Minecraft using **Python**, **OpenCV**, **MediaPipe**, and **PyQt6**. Control Minecraft actions via hand gestures captured from your webcam or IP camera.

---

## 🎯 Features

- Real-time hand tracking with MediaPipe
- Webcam & IP camera support
- Optional visualizations: hand connections & landmark numbers
- User-friendly GUI with PyQt6
- Cross-platform support (Windows/Linux/macOS)
- Prebuilt Windows version for quick start

---

## 🚀 Getting Started

### 1️⃣ Run Prebuilt Windows Version
- Navigate to the `bin` folder.
- Download `Minecraft-Hand-Controller-ORUCEXE`.
- Extract and run `MC Hand Controller.exe`.
- No need to install Python, PyQt6, or other dependencies.

---

### 2️⃣ Build from Source

**Requirements:**
- Python 3.9-3.11
- PyQt6
- OpenCV
- MediaPipe
- pygrabber
- keyboard

**Steps:**
```bash
git clone https://github.com/orucexe/Minecraft-Hand-Controller_ORUCEXE.git
cd Minecraft-Hand-Controller
python -m venv myenv
myenv\Scripts\activate        # Windows
source myenv/bin/activate     # Linux/macOS
pip install -r requirements.txt
python app.py
