from flask import Flask, render_template, send_from_directory, jsonify
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Configure root logger to show all messages in console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def ensure_dir(file_path):
    """Make sure the directory for a file exists"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def setup_file_logging(log_path):
    """Set up file logging with proper directory creation"""
    try:
        ensure_dir(log_path)
        handler = RotatingFileHandler(log_path, maxBytes=10240, backupCount=3)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(handler)
        logger.info(f"File logging setup successfully at: {log_path}")
    except Exception as e:
        logger.error(f"Failed to setup file logging: {e}")

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            base_path = sys._MEIPASS
            log_path = os.path.dirname(sys.executable)
            print(f"Running from frozen application. Base path: {base_path}")
        else:
            # Running in normal Python environment
            base_path = os.path.abspath(os.path.dirname(__file__))
            log_path = base_path
            print(f"Running from Python environment. Base path: {base_path}")
        
        # Set up logging
        log_file = os.path.join(log_path, 'flask_app.log')
        setup_file_logging(log_file)
        
        full_path = os.path.join(base_path, relative_path)
        print(f"Resource path for {relative_path}: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error getting resource path: {e}")
        logger.error(f"Error getting resource path: {e}")
        return relative_path

print("Starting Flask application setup...")
# Initialize Flask with correct template and static folders
template_dir = get_resource_path('templates')
static_dir = get_resource_path('static')

print(f"Template directory: {template_dir}")
print(f"Static directory: {static_dir}")

app = Flask(__name__,
           template_folder=template_dir,
           static_folder=static_dir)

@app.route('/')
def index():
    app.logger.info('Accessing root route')
    try:
        template_list = os.listdir(template_dir)
        app.logger.info(f'Available templates: {template_list}')
        return render_template('config.html', videos=[{'name': '', 'path': ''} for _ in range(12)])
    except Exception as e:
        app.logger.error(f'Error rendering template: {e}')
        return f'Error: {str(e)}', 500

@app.route('/config')
def config():
    app.logger.info('Accessing config route')
    try:
        template_list = os.listdir(template_dir)
        app.logger.info(f'Available templates: {template_list}')
        return render_template('config.html', videos=[{'name': '', 'path': ''} for _ in range(12)])
    except Exception as e:
        app.logger.error(f'Error rendering template: {e}')
        return f'Error: {str(e)}', 500

@app.route('/playback')
def playback():
    app.logger.info('Accessing playback route')
    try:
        return render_template('playback.html')
    except Exception as e:
        app.logger.error(f'Error rendering template: {e}')
        return f'Error: {str(e)}', 500

@app.route('/stats')
def stats():
    app.logger.info('Accessing stats route')
    try:
        return render_template('stats.html')
    except Exception as e:
        app.logger.error(f'Error rendering template: {e}')
        return f'Error: {str(e)}', 500

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    try:
        return send_from_directory('static/uploads', filename)
    except Exception as e:
        app.logger.error(f'Error serving upload: {e}')
        return f'Error: {str(e)}', 404

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {error}')
    return 'Page not found. Available routes: /, /config, /playback, /stats', 404

@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f'An error occurred: {error}')
    return jsonify({'error': str(error)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False, port=5000)