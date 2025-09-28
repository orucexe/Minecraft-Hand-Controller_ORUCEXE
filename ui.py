import os
import sys
import cv2
import mediapipe
import threading
import platform
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout,
    QPushButton, QComboBox, QHBoxLayout,
    QSizePolicy, QLineEdit, QCheckBox
)
from PyQt6.QtGui import QImage, QPixmap, QPalette, QColor, QIcon
from PyQt6.QtCore import QTimer, Qt
from pygrabber.dshow_graph import FilterGraph
from hand_controller import process_frame, set_camera

def run_ui():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    app.setPalette(palette)

    window = QWidget()
    window.setWindowTitle("MINECRAFT HAND CONTROLLER - ORUCEXE")
    layout = QVBoxLayout()
    icon_path = "assets/icon.ico"
    app.setWindowIcon(QIcon(icon_path))
    window.setWindowIcon(QIcon(icon_path))

    # Video label
    video_label = QLabel("Camera not started")
    video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    video_label.setStyleSheet(
        "background-color: black; border: 2px solid #555; color: white; font-size: 16px;"
    )
    video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    video_label.setMinimumSize(320, 240)
    layout.addWidget(video_label)

    # Text label
    text_label = QLabel("")
    text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    text_label.setStyleSheet(
        "color: #FFD700; font-size: 18px; font-weight: bold; background-color: rgba(0,0,0,0);"
    )
    text_label.setFixedHeight(30)
    layout.addWidget(text_label)

    # Controller
    controls_layout = QHBoxLayout()
    camera_box = QComboBox()
    camera_box.setStyleSheet("""
        QComboBox {
            padding: 5px;
            border-radius: 5px;
            background-color: #444;
            color: white;
        }
        QComboBox QAbstractItemView {
            background-color: #222;
            color: white;
            selection-background-color: #555;
        }
    """)
    controls_layout.addWidget(camera_box)

    ip_input = QLineEdit()
    ip_input.setPlaceholderText("Enter IP Camera URL")
    ip_input.setStyleSheet("background-color: #444; color: white; padding: 5px; border-radius: 5px;")
    ip_input.setVisible(False)
    controls_layout.addWidget(ip_input)

    # Landmark lines and numbers
    checkbox_layout = QHBoxLayout()
    checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    draw_lines_cb = QCheckBox("Draw Hand Connections")
    draw_lines_cb.setStyleSheet("color: white;")

    draw_numbers_cb = QCheckBox("Show Landmark Numbers")
    draw_numbers_cb.setStyleSheet("color: white;")

    checkbox_layout.addWidget(draw_lines_cb)
    checkbox_layout.addWidget(draw_numbers_cb)

    layout.addLayout(checkbox_layout)


    start_btn = QPushButton("Start")
    start_btn.setStyleSheet("""
        QPushButton {
            background-color: #28a745;
            color: white;
            padding: 8px;
            border-radius: 8px;
        }
        QPushButton:hover { background-color: #34d058; }
        QPushButton:pressed { background-color: #1e7e34; }
    """)

    stop_btn = QPushButton("Stop")
    stop_btn.setStyleSheet("""
        QPushButton {
            background-color: #dc3545;
            color: white;
            padding: 8px;
            border-radius: 8px;
        }
        QPushButton:hover { background-color: #e55361; }
        QPushButton:pressed { background-color: #a71d2a; }
    """)

    controls_layout.addWidget(start_btn)
    controls_layout.addWidget(stop_btn)
    layout.addLayout(controls_layout)

    start_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    stop_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    camera_box.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    ip_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
    draw_lines_cb.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    draw_numbers_cb.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    # List cameras
    if platform.system() == "Windows": # For Windows(camera names)
        graph = FilterGraph()
        devices = graph.get_input_devices()
        for i, name in enumerate(devices):
            camera_box.addItem(name, i)
    else:
        # Linux/macOS(only index)
        for i in range(7):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                camera_box.addItem(f"Camera {i}", i)
                cap.release()
    camera_box.addItem("IP Camera", -1)

    def on_camera_change(index):
        ip_input.setVisible(camera_box.currentData() == -1)
    camera_box.currentIndexChanged.connect(on_camera_change)

    window.setLayout(layout)
    window.resize(670, 614)

    def closeEvent(event):
        nonlocal running, camera_thread
        running = False
        if camera_thread is not None:
            camera_thread.join()
        event.accept()

    window.closeEvent = closeEvent

    window.show()

    # Frame reading with Thread
    camera_thread = None
    running = False
    lock = threading.Lock()
    frame = None
    frame_text = ""

    def camera_loop():
        nonlocal frame, frame_text, running
        while running:
            img, text = process_frame(
                draw_lines=draw_lines_cb.isChecked(),
                draw_numbers=draw_numbers_cb.isChecked()
            )
            if img is None:
                continue
            img = cv2.resize(img, (640, 480))
            with lock:
                frame = img
                frame_text = text


    timer = QTimer()

    def update_ui():
        nonlocal frame, frame_text
        with lock:
            if frame is None:
                return
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = img_rgb.shape
            qimg = QImage(img_rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg).scaled(
                video_label.width(), video_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            video_label.setPixmap(pixmap)
            text_label.setText(frame_text)

    timer.timeout.connect(update_ui)

    # Start/Stop
    def start_camera():
        nonlocal running, camera_thread
        cam_data = camera_box.currentData()
        video_label.setText("Connecting to camera...")
        text_label.setText("")
        set_camera(ip_input.text().strip() if cam_data == -1 else cam_data)
        running = True
        camera_thread = threading.Thread(target=camera_loop, daemon=True)
        camera_thread.start()
        timer.start(30)

    def stop_camera():
        nonlocal running
        running = False
        video_label.setText("Camera stopped")
        text_label.setText("")

    start_btn.clicked.connect(start_camera)
    stop_btn.clicked.connect(stop_camera)

    sys.exit(app.exec())
