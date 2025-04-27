import cv2
import time
import numpy as np

class VideoPlayer:
    """Class for video playback operations using OpenCV"""
    
    def __init__(self, video_path=None):
        """
        Initialize the video player
        
        Args:
            video_path (str, optional): Path to the video file
        """
        self.video_path = video_path
        self.cap = None
        self.frame_count = 0
        self.fps = 0
        self.current_frame = 0
        
        if video_path:
            self.load_video(video_path)
    
    def load_video(self, video_path):
        """
        Load a video file
        
        Args:
            video_path (str): Path to the video file
            
        Returns:
            bool: True if video loaded successfully, False otherwise
        """
        # Close any existing video
        if self.cap:
            self.cap.release()
        
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            return False
        
        # Get video properties
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.current_frame = 0
        
        return True
    
    def get_frame(self):
        """
        Get the current frame
        
        Returns:
            numpy.ndarray or None: The current frame, or None if no frame or error
        """
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        
        if ret:
            self.current_frame += 1
            return frame
        else:
            return None
    
    def seek(self, frame_number):
        """
        Seek to a specific frame
        
        Args:
            frame_number (int): The frame number to seek to
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.cap or frame_number >= self.frame_count:
            return False
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame = frame_number
        return True
    
    def get_total_duration(self):
        """
        Get the total duration of the video in seconds
        
        Returns:
            float: Duration in seconds
        """
        if not self.cap or self.fps == 0:
            return 0
        
        return self.frame_count / self.fps
    
    def get_current_time(self):
        """
        Get the current playback time in seconds
        
        Returns:
            float: Current time in seconds
        """
        if not self.cap or self.fps == 0:
            return 0
        
        return self.current_frame / self.fps
    
    def release(self):
        """Release video resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
