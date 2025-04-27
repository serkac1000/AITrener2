import os
import json

class VideoConfig:
    """Class to handle saving and loading video configurations"""
    
    CONFIG_FILE = "video_config.json"
    
    @staticmethod
    def save_videos(videos):
        """
        Save video configurations to a JSON file
        
        Args:
            videos (list): List of dictionaries containing video name and path
        """
        with open(VideoConfig.CONFIG_FILE, 'w') as f:
            json.dump(videos, f, indent=4)
    
    @staticmethod
    def load_videos():
        """
        Load video configurations from a JSON file
        
        Returns:
            list: List of dictionaries containing video name and path
                  Returns empty list if file doesn't exist
        """
        if not os.path.exists(VideoConfig.CONFIG_FILE):
            # Return empty configurations for 12 videos
            return [{"name": "", "path": ""} for _ in range(12)]
        
        with open(VideoConfig.CONFIG_FILE, 'r') as f:
            videos = json.load(f)
            
        # Ensure we always have exactly 12 videos
        if len(videos) < 12:
            videos.extend([{"name": "", "path": ""} for _ in range(12 - len(videos))])
        elif len(videos) > 12:
            videos = videos[:12]
            
        return videos
