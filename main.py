"""
Libraries
"""
import sys
import cv2
import numpy as np
import pyautogui
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush

# Screen Recorder Class
class ScreenRecorder(QWidget):
    def __init__(self):
        # Initialization
        super().__init__()
        self.initUI()
        self.recording = False
        self.out = None
        self.fps = 10
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_frame)
        self.output_directory = r"C:\Users\Shakir Salam\PycharmProjects\qrec\output"
        self.output_file = ""
        self.dragPosition = None

        # Set Window Properties
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def initUI(self):
        self.setWindowTitle("QRec")
        self.setGeometry(150, 150, 150, 150)

        # Title Label with App Name
        self.title_label = QLabel("QRec")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #FFFFFF; background-color: transparent;")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Close Button
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet(
            """
            QPushButton 
            {
                background-color: #FF4444;
                color: white;
                font-weight: bold;
                border-radius: 15px;
                border: none;
            }
            
            QPushButton:hover
            {
                background-color: #FF6666;
            }
            """
        )

        # Record Button
        self.record_button = QPushButton("START")
        self.record_button.setCheckable(True)
        self.record_button.setFixedSize(120, 120)
        self.record_button.setStyleSheet(
            """
            QPushButton
            {
                background-color: #44CC44;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border_radius: 75px;
                border: 2px solid #228822;
            }
            
            QPushButton:checked
            {
                background-color: #FF4444;
            }
            
            QPushButton:hover
            {
                background-color: #66DD66;
            }
            
            QPushButton:checked:hover
            {
                background-color: #FF6666;
            }  
            """
        )

        # Directory Button
        self.open_directory_button = QPushButton("Open Files")
        self.open_directory_button.setFixedHeight(30)
        self.open_directory_button.setStyleSheet(
            """
            QPushButton
            {
                background-color: #4466CC;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                border: 2px solid #2244AA;
            }
            
            QPushButton
            {
                background-color: #5577DD;
            }
            """
        )

        # Status Indicator
        self.status_label = QLabel("Ready to Record")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet(
            """
                background-color: transparent;
                color: #AAAAAA;
            """
        )
        self.status_label.setAlignment(Qt.AlignCenter)

        # Decorative Lines
        # Deco Line 1
        self.deco_line1 = QFrame()
        self.deco_line1.setFrameShape(QFrame.HLine)
        self.deco_line1.setStyleSheet(
            """
                background-color: #666666;
            """
        )
        self.deco_line1.setFixedHeight(2)
        # Deco Line 2
        self.deco_line2 = QFrame()
        self.deco_line2.setFrameShape(QFrame.HLine)
        self.deco_line2.setStyleSheet(
            """
                background-color: #666666;
            """
        )
        self.deco_line2.setFixedHeight(2)

        # Header Layout
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.close_button)

        # Main Layout
        layout = QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(self.deco_line1)
        # Spacer
        layout.addWidget(QLabel(""))
        layout.addWidget(self.record_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel(""))
        layout.addWidget(self.deco_line2)
        layout.addWidget(self.open_directory_button)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        # Clicked Connect
        self.close_button.clicked.connect(self.close)
        self.record_button.clicked.connect(self.toggle_recording)
        self.open_directory_button.clicked.connect(self.open_output_directory)

    # Drag Mouse Position Event
    def paintEvent(self, event):
        # Draw rounded rectangle
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Create rounded rectangle
        painter.setPen(QPen(QColor(40, 40, 40), 2))
        painter.setBrush(QBrush(QColor(40, 40, 40, 120)))
        painter.drawRoundedRect(self.rect(), 20, 20)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPosition:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    # Toggle Recording
    def toggle_recording(self):
        if self.record_button.isChecked():
            self.start_recording()
            self.record_button.setText("Stop")
            self.status_label.setText("Recording")
            self.status_label.setStyleSheet(
                """
                    background-color: transparent;
                    color: #FF5555;
                """
            )
        else:
            self.stop_recording()
            self.record_button.setText("Start")
            self.status_label.setText("Recording Saved")
            self.status_label.setStyleSheet(
                """
                    background-color: transparent;
                    color: #55FF55
                """
            )
            # Reset to ready status after 3 seconds
            QTimer.singleShot(3000, lambda:self.update_status_ready())

    def update_status_ready(self):
        self.status_label.setText("Ready to Record")
        self.status_label.setStyleSheet(
            """
                background-color: transparent;
                color: #AAAAAA
            """
        )

    # Start Recording
    def start_recording(self):
        if not self.recording:
            try:
                self.output_file = os.path.join(self.output_directory, "output.avi")
                self.recording = True
                screen_size = pyautogui.size()
                self.out = cv2.VideoWriter(self.output_file, cv2.VideoWriter_fourcc(*"XVID"), self.fps, screen_size)
                self.timer.start(int(1000 / self.fps))
            except Exception as e:
                print(f"Error start recording {e}")
                self.recording = False
                self.record_button.setChecked(False)
                self.record_button.setText("Start")
                self.status_label.setText("Error: " + str(e)[:30])
                self.status_label.setStyleSheet(
                    """
                        background-color:transparent;
                        color: #FF5555;   
                    """
                )

    # Capture Frame
    def capture_frame(self):
        if self.recording:
            try:
                frame = pyautogui.screenshot()
                frame = np.array(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                self.out.write(frame)
            except Exception as e:
                print(f"Error in capture frame: {e}")
                self.stop_recording()
                self.status_label.setText("Error Capturing Frame")
                self.status_label.setStyleSheet(
                    """
                        background-color: transparent;
                        color: #FF5555;
                    """
                )

    def stop_recording(self):
        if self.recording:
            try:
                self.recording = False
                self.timer.stop()
                if self.out:
                    self.out.release()
                print(f"Recording is saved to {self.output_file}")
            except Exception as e:
                print(f"Error stop recording: {e}")

    def open_output_directory(self):
        try:
            if os.path.exists(self.output_directory):
                subprocess.Popen(
                    f"explorer {self.output_directory}"
                    if os.name == 'nt' else ['xdg-open', self.output_directory])
            else:
                self.status_label.setText("Directory Not Found")
                self.status_label.setStyleSheet(
                    """
                        background-color: transparent;
                        color: #FF5555
                    """
                )
        except Exception as e:
            print(f"Failed to Open Directory: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorder()
    window.show()
    sys.exit(app.exec())







































