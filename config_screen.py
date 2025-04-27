import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QPushButton, QFileDialog, 
                           QScrollArea, QFrame, QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from video_config import VideoConfig
from playback_screen import PlaybackScreen

class ConfigScreen(QMainWindow):
    """Configuration screen for setting up video names and paths"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Video Player - Configuration")
        self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()
        self.load_saved_config()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Configure Your Videos")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Set names and file paths for 12 videos. You can browse for videos or enter paths directly.")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # Scroll area for video configurations
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        self.video_widgets = []
        
        # Create 12 video configuration rows
        for i in range(12):
            video_frame = QFrame()
            video_frame.setFrameShape(QFrame.StyledPanel)
            video_layout = QGridLayout(video_frame)
            
            # Video number
            number_label = QLabel(f"Video {i+1}:")
            number_label.setFont(QFont("Arial", 10, QFont.Bold))
            
            # Video name
            name_label = QLabel("Name:")
            name_input = QLineEdit()
            name_input.setPlaceholderText("Enter video name")
            
            # Video path
            path_label = QLabel("File Path:")
            path_input = QLineEdit()
            path_input.setPlaceholderText("Enter file path or browse")
            
            # Browse button
            browse_button = QPushButton("Browse...")
            browse_button.clicked.connect(lambda checked, idx=i: self.browse_video(idx))
            
            # Add widgets to layout
            video_layout.addWidget(number_label, 0, 0)
            video_layout.addWidget(name_label, 1, 0)
            video_layout.addWidget(name_input, 1, 1, 1, 2)
            video_layout.addWidget(path_label, 2, 0)
            video_layout.addWidget(path_input, 2, 1)
            video_layout.addWidget(browse_button, 2, 2)
            
            scroll_layout.addWidget(video_frame)
            
            # Store references to input fields
            self.video_widgets.append({
                "name_input": name_input,
                "path_input": path_input
            })
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Configuration")
        save_button.setFont(QFont("Arial", 11))
        save_button.clicked.connect(self.save_configuration)
        
        continue_button = QPushButton("Continue to Playback")
        continue_button.setFont(QFont("Arial", 11))
        continue_button.clicked.connect(self.open_playback_screen)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(continue_button)
        
        main_layout.addLayout(button_layout)
    
    def browse_video(self, video_index):
        """Open file dialog to browse for a video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Video File", 
            "", 
            "Video Files (*.mp4)"
        )
        
        if file_path:
            self.video_widgets[video_index]["path_input"].setText(file_path)
            
            # If name is empty, use the filename (without extension) as the name
            name_input = self.video_widgets[video_index]["name_input"]
            if not name_input.text():
                file_name = os.path.basename(file_path)
                name_without_ext = os.path.splitext(file_name)[0]
                name_input.setText(name_without_ext)
    
    def save_configuration(self):
        """Save the current video configuration"""
        videos = []
        
        for widget in self.video_widgets:
            name = widget["name_input"].text().strip()
            path = widget["path_input"].text().strip()
            
            videos.append({
                "name": name,
                "path": path
            })
        
        VideoConfig.save_videos(videos)
        
        QMessageBox.information(
            self,
            "Configuration Saved",
            "Your video configuration has been saved successfully."
        )
    
    def load_saved_config(self):
        """Load previously saved configuration (if exists)"""
        videos = VideoConfig.load_videos()
        
        for i, video in enumerate(videos):
            if i < len(self.video_widgets):
                self.video_widgets[i]["name_input"].setText(video["name"])
                self.video_widgets[i]["path_input"].setText(video["path"])
    
    def open_playback_screen(self):
        """Open the playback screen"""
        # First save the current configuration
        self.save_configuration()
        
        # Open the playback screen
        self.playback_screen = PlaybackScreen()
        self.playback_screen.show()
        self.hide()  # Hide the configuration screen
