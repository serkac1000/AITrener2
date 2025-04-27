# Video Player Desktop Application

A powerful desktop video player application built with Python, PyQt5, and OpenCV, featuring slow-motion playback and video analysis capabilities.

## Features

- **Video Configuration**
  - Configure up to 12 different videos
  - Custom naming for each video
  - Easy file browsing and path management

- **Video Playback**
  - Smooth video playback with play/pause functionality
  - Variable speed control (0.1x to 1.0x speed)
  - Progress bar with time display
  - Video selection dropdown menu
  - High-quality video rendering
  - 16:9 aspect ratio display area

- **Playback Controls**
  - Play/Pause button
  - Stop button (resets to beginning)
  - Speed slider for adjusting playback speed
  - Progress slider for seeking through video
  - Current time and total duration display

- **User Interface**
  - Clean and intuitive interface
  - Easy navigation between configuration and playback screens
  - Video progress tracking
  - Real-time speed adjustment display

## Installation

The application is distributed as a standalone executable created with PyInstaller. You can find the executable in the `dist` folder.

### Running from Executable

1. Navigate to the `dist` folder
2. Find the `VideoPlayerDesktop.exe` file
3. Double-click to run the application

### System Requirements

- Windows operating system
- No additional software installation required (standalone executable)
- Sufficient disk space for video files
- Recommended minimum 4GB RAM for smooth playback

## Usage

1. **First Launch**
   - When you first open the application, you'll see the configuration screen
   - Configure your videos by setting names and paths for each video slot
   - Use the "Browse" buttons to easily locate video files

2. **Configuring Videos**
   - Enter a name for each video
   - Set the video path using the browse button or direct input
   - Save your configuration using the "Save Configuration" button

3. **Playing Videos**
   - Click "Continue to Playback" to open the playback screen
   - Select a video from the dropdown menu
   - Use the play/pause button to control playback
   - Adjust playback speed using the slider (0.1x to 1.0x)
   - Use the progress bar to seek through the video
   - Stop button resets the video to the beginning

4. **Navigation**
   - Use "Back to Configuration" to return to the config screen
   - Close the window to exit the application

## Supported Video Formats

The application supports common video formats including:
- MP4
- AVI
- MOV
- Other formats supported by OpenCV

## File Management

Videos can be stored anywhere on your system. The application saves the video configurations for future use, so you don't need to reconfigure them every time you start the application.

## Troubleshooting

- If a video doesn't play, verify the file path is correct
- Ensure the video file format is supported
- Check that you have sufficient system resources for playback
- Make sure the video file isn't corrupted or in use by another application

## Technical Details

Built with:
- Python
- PyQt5 for the GUI
- OpenCV for video processing
- Flask for web interface components
- Custom video tracking and analysis features