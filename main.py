from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QMainWindow, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, QTimer
import sys
import os
import threading
import time
import subprocess
import logging
import requests
from datetime import datetime
import traceback

def debug_print(message):
    """Print debug message to both console and file"""
    print(message)
    try:
        if getattr(sys, 'frozen', False):
            debug_file = os.path.join(os.path.dirname(sys.executable), 'debug.txt')
        else:
            debug_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug.txt')
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: {message}\n")
    except Exception as e:
        print(f"Error writing to debug file: {e}")

debug_print(f"Starting application at {datetime.now()}")
debug_print(f"Python executable: {sys.executable}")
debug_print(f"Working directory: {os.getcwd()}")

if getattr(sys, 'frozen', False):
    debug_print("Running in PyInstaller bundle")
    base_dir = sys._MEIPASS
    app_dir = os.path.dirname(sys.executable)
else:
    debug_print("Running in Python environment")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = base_dir

debug_print(f"Base directory: {base_dir}")
debug_print(f"App directory: {app_dir}")

# Kill any existing instances of the application
debug_print("Checking for existing instances...")
try:
    subprocess.run(['taskkill', '/F', '/IM', 'VideoPlayerDesktop.exe'], 
                  stdout=subprocess.PIPE, 
                  stderr=subprocess.PIPE)
    debug_print("Cleaned up existing instances.")
except Exception as e:
    debug_print(f"No existing instances found: {e}")

debug_print("Initializing video player application...")

# Import flask app after setup
from web_app import app

def wait_for_server(url, timeout=10):
    """Wait for server to start"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                debug_print("Server is responding successfully")
                return True
        except requests.exceptions.RequestException as e:
            debug_print(f"Server not ready yet: {e}")
            time.sleep(0.5)
    debug_print("Server failed to start within timeout period")
    return False

class ConfigScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowTitle("Video Player")
            self.setGeometry(100, 100, 800, 600)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Configure QWebEngineView
            profile = QWebEngineProfile.defaultProfile()
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
            
            self.web_view = QWebEngineView()
            layout.addWidget(self.web_view)

            # Start Flask in a separate thread
            debug_print("Starting Flask server thread...")
            self.flask_thread = threading.Thread(target=self.run_flask, daemon=True)
            self.flask_thread.start()

            # Check server status periodically
            self.check_timer = QTimer(self)
            self.check_timer.timeout.connect(self.check_server_and_load)
            self.check_timer.start(1000)  # Check every second

            debug_print("GUI initialized successfully")
        except Exception as e:
            debug_print(f"Error initializing GUI: {e}")
            debug_print(f"Traceback: {traceback.format_exc()}")
            self.show_error("Initialization Error", str(e))

    def check_server_and_load(self):
        """Check if server is running and load the URL"""
        debug_print("Checking if server is running...")
        if wait_for_server('http://127.0.0.1:5000', timeout=2):
            debug_print("Server is running, loading URL...")
            self.load_url()
            self.check_timer.stop()  # Stop checking once server is running
        else:
            debug_print("Server not responding yet...")

    def load_url(self):
        try:
            debug_print("Loading web interface...")
            self.web_view.setUrl(QUrl("http://127.0.0.1:5000"))
            debug_print("URL loaded into web view")
        except Exception as e:
            debug_print(f"Error loading URL: {e}")
            debug_print(f"Traceback: {traceback.format_exc()}")
            self.show_error("Loading Error", str(e))

    def run_flask(self):
        try:
            debug_print("Starting Flask server...")
            debug_print(f"Template directory: {os.path.join(base_dir, 'templates')}")
            debug_print(f"Static directory: {os.path.join(base_dir, 'static')}")
            debug_print(f"Current working directory: {os.getcwd()}")
            app.run(debug=False, port=5000, use_reloader=False)
        except Exception as e:
            debug_print(f"Flask server error: {e}")
            debug_print(f"Traceback: {traceback.format_exc()}")
            self.show_error("Server Error", str(e))

    def show_error(self, title, message):
        debug_print(f"Error - {title}: {message}")
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        try:
            debug_print("Application closing...")
            self.web_view.setUrl(QUrl("about:blank"))
            event.accept()
        except Exception as e:
            debug_print(f"Error during cleanup: {e}")
            debug_print(f"Traceback: {traceback.format_exc()}")

def main():
    try:
        qt_app = QApplication(sys.argv)
        window = ConfigScreen()
        window.show()
        debug_print("Application started successfully")
        return qt_app.exec_()
    except Exception as e:
        debug_print(f"Application error: {e}")
        debug_print(f"Traceback: {traceback.format_exc()}")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        debug_print(f"Fatal error: {e}")
        debug_print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)