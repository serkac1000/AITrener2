from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QComboBox, QSlider, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QFont
import cv2
import numpy as np

from video_config import VideoConfig

class PlaybackScreen(QMainWindow):
    """Screen for playing videos with slow motion functionality"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Video Player - Playback")
        self.setGeometry(100, 100, 1000, 700)
        
        # Video playback variables
        self.video_path = None
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.playback_speed = 1.0  # Normal speed
        self.is_playing = False
        
        self.init_ui()
        self.load_videos()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Video Playback")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Video selection combo box
        selection_layout = QHBoxLayout()
        
        selection_label = QLabel("Select Video:")
        selection_label.setFont(QFont("Arial", 11))
        
        self.video_combo = QComboBox()
        self.video_combo.setMinimumWidth(400)
        self.video_combo.currentIndexChanged.connect(self.video_selected)
        
        selection_layout.addWidget(selection_label)
        selection_layout.addWidget(self.video_combo)
        selection_layout.addStretch()
        
        main_layout.addLayout(selection_layout)
        
        # Video display area
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(800, 450)  # 16:9 aspect ratio
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setText("No video selected")
        self.video_label.setFont(QFont("Arial", 14))
        self.video_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(self.video_label)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)
        self.play_button.setEnabled(False)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_video)
        self.stop_button.setEnabled(False)
        
        # Slow motion controls
        speed_label = QLabel("Playback Speed:")
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)  # 0.1x speed
        self.speed_slider.setMaximum(100)  # 1.0x speed
        self.speed_slider.setValue(100)  # Default to normal speed
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.speed_changed)
        
        self.speed_value_label = QLabel("1.0x")
        
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(speed_label)
        controls_layout.addWidget(self.speed_slider)
        controls_layout.addWidget(self.speed_value_label)
        
        main_layout.addLayout(controls_layout)
        
        # Progress bar/slider
        progress_layout = QHBoxLayout()
        
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setEnabled(False)
        self.progress_slider.sliderMoved.connect(self.set_position)
        
        self.time_label = QLabel("00:00 / 00:00")
        
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.time_label)
        
        main_layout.addLayout(progress_layout)
        
        # Back to config button
        button_layout = QHBoxLayout()
        
        back_button = QPushButton("Back to Configuration")
        back_button.clicked.connect(self.go_back_to_config)
        
        button_layout.addStretch()
        button_layout.addWidget(back_button)
        
        main_layout.addLayout(button_layout)
    
    def load_videos(self):
        """Load the saved video configurations into the combo box"""
        videos = VideoConfig.load_videos()
        
        # Filter out videos with empty names or paths
        valid_videos = [video for video in videos if video["name"] and video["path"]]
        
        if not valid_videos:
            self.video_combo.addItem("No videos configured")
            self.video_combo.setEnabled(False)
            return
        
        for video in valid_videos:
            self.video_combo.addItem(f"{video['name']}", video["path"])
    
    def video_selected(self, index):
        """Handle video selection from combo box"""
        if index < 0 or not self.video_combo.isEnabled():
            return
        
        # Stop any currently playing video
        self.stop_video()
        
        # Get the selected video path from combo box data
        self.video_path = self.video_combo.currentData()
        
        # Open the video file
        if self.video_path:
            try:
                self.cap = cv2.VideoCapture(self.video_path)
                
                if not self.cap.isOpened():
                    QMessageBox.warning(
                        self,
                        "Video Error",
                        f"Could not open video file: {self.video_path}"
                    )
                    return
                
                # Get video properties
                self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                
                # Set up progress slider
                self.progress_slider.setMinimum(0)
                self.progress_slider.setMaximum(self.frame_count - 1)
                self.progress_slider.setValue(0)
                self.progress_slider.setEnabled(True)
                
                # Update UI
                self.play_button.setEnabled(True)
                self.stop_button.setEnabled(True)
                
                # Show first frame
                ret, frame = self.cap.read()
                if ret:
                    self.display_frame(frame)
                
                # Update time label
                total_time = self.frame_count / self.fps
                self.time_label.setText(f"00:00 / {self.format_time(total_time)}")
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while opening the video: {str(e)}"
                )
    
    def toggle_play(self):
        """Toggle between play and pause"""
        if not self.cap:
            return
        
        if self.is_playing:
            # Pause video
            self.timer.stop()
            self.play_button.setText("Play")
            self.is_playing = False
        else:
            # Play video
            # Set timer interval based on playback speed
            interval = int(1000 / (self.fps * self.playback_speed))
            self.timer.start(interval)
            self.play_button.setText("Pause")
            self.is_playing = True
    
    def stop_video(self):
        """Stop video playback and reset to beginning"""
        if self.timer.isActive():
            self.timer.stop()
        
        self.is_playing = False
        self.play_button.setText("Play")
        
        # Reset position
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
            
            self.progress_slider.setValue(0)
            self.time_label.setText(f"00:00 / {self.format_time(self.frame_count / self.fps)}")
    
    def update_frame(self):
        """Update video frame during playback"""
        if not self.cap:
            return
        
        # Read the next frame
        ret, frame = self.cap.read()
        
        if not ret:
            # End of video
            self.timer.stop()
            self.play_button.setText("Play")
            self.is_playing = False
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Rewind
            return
        
        # Display the frame
        self.display_frame(frame)
        
        # Update progress
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.progress_slider.setValue(current_frame)
        
        # Update time label
        current_time = current_frame / self.fps
        total_time = self.frame_count / self.fps
        self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(total_time)}")
    
    def display_frame(self, frame):
        """Convert OpenCV frame to QPixmap and display it"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Calculate scaled dimensions (maintaining aspect ratio)
        h, w, ch = rgb_frame.shape
        label_w = self.video_label.width()
        label_h = self.video_label.height()
        
        # Choose the scaling factor that fits both dimensions
        scale_w = label_w / w
        scale_h = label_h / h
        scale = min(scale_w, scale_h)
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize the frame
        rgb_frame = cv2.resize(rgb_frame, (new_w, new_h))
        
        # Create QImage from the frame
        bytes_per_line = ch * new_w
        q_img = QImage(rgb_frame.data, new_w, new_h, bytes_per_line, QImage.Format_RGB888)
        
        # Convert to QPixmap and display
        pixmap = QPixmap.fromImage(q_img)
        self.video_label.setPixmap(pixmap)
    
    def speed_changed(self, value):
        """Handle playback speed slider change"""
        # Convert slider value to playback speed (0.1x to 1.0x)
        self.playback_speed = value / 100.0
        self.speed_value_label.setText(f"{self.playback_speed:.1f}x")
        
        # Update timer interval if video is playing
        if self.is_playing and self.cap:
            self.timer.stop()
            interval = int(1000 / (self.fps * self.playback_speed))
            self.timer.start(interval)
    
    def set_position(self, position):
        """Set video position when user moves the progress slider"""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            
            # Update the time label
            current_time = position / self.fps
            total_time = self.frame_count / self.fps
            self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(total_time)}")
            
            # Show the frame at the new position
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                # Move back one frame since read() advances the frame
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
    
    def format_time(self, seconds):
        """Format seconds as MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def go_back_to_config(self):
        """Return to the configuration screen"""
        # Stop video playback
        self.stop_video()
        
        # Release video resources
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Import here to avoid circular imports
        from config_screen import ConfigScreen
        
        # Open the config screen
        self.config_screen = ConfigScreen()
        self.config_screen.show()
        self.close()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop video playback and release resources
        if self.timer.isActive():
            self.timer.stop()
        
        if self.cap:
            self.cap.release()
        
        event.accept()
