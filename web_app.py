from flask import Flask, render_template, send_from_directory, jsonify, request, Response
import os
import sys
import json
import uuid
import logging
import re
import mimetypes
from logging.handlers import RotatingFileHandler
from werkzeug.utils import secure_filename

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
        # Load video configurations from video_config.json
        videos = []
        config_file = os.path.join(static_dir, 'video_config.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    videos = json.load(f)
                app.logger.info(f'Loaded {len(videos)} videos from config')
            except Exception as e:
                app.logger.error(f'Error loading video config: {e}')
        
        # Filter out empty entries
        valid_videos = []
        for video in videos:
            if video.get('name') and video.get('path'):
                # The path in config is already in the correct format (/uploads/...)
                valid_videos.append(video)
        
        app.logger.info(f'Found {len(valid_videos)} valid videos')
        return render_template('playback.html', videos=valid_videos)
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

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not file.filename.endswith('.mp4'):
            return jsonify({'error': 'Only MP4 files are allowed'}), 400
        
        # Generate a unique filename
        filename = str(uuid.uuid4()) + '.mp4'
        upload_folder = os.path.join(static_dir, 'uploads')
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Return the relative path that can be used in video src
        relative_path = f'/uploads/{filename}'
        return jsonify({'path': relative_path}), 200
        
    except Exception as e:
        app.logger.error(f'Upload error: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    try:
        upload_folder = os.path.join(static_dir, 'uploads')
        video_path = os.path.join(upload_folder, filename)
        
        app.logger.info(f'Attempting to serve video: {filename}')
        app.logger.info(f'Full path: {video_path}')
        
        # Check if file exists
        if not os.path.isfile(video_path):
            app.logger.error(f'Video file not found: {video_path}')
            return 'Video not found', 404
            
        # Get file size
        file_size = os.path.getsize(video_path)
        app.logger.info(f'Video file size: {file_size} bytes')
        
        # Handle range requests
        range_header = request.headers.get('Range')
        
        # Set standard headers
        headers = {
            'Accept-Ranges': 'bytes',
            'Content-Type': 'video/mp4',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        if range_header:
            app.logger.info(f'Range request: {range_header}')
            byte1, byte2 = 0, None
            match = re.search(r'(\d+)-(\d*)', range_header)
            groups = match.groups()
            
            if groups[0]:
                byte1 = int(groups[0])
            if groups[1]:
                byte2 = int(groups[1])
            
            if byte2 is None:
                byte2 = file_size - 1
            length = byte2 - byte1 + 1
            
            with open(video_path, 'rb') as f:
                f.seek(byte1)
                data = f.read(length)
            
            headers.update({
                'Content-Range': f'bytes {byte1}-{byte2}/{file_size}',
                'Content-Length': str(length)
            })
            
            return Response(
                data,
                206,
                mimetype='video/mp4',
                direct_passthrough=True,
                headers=headers
            )
        
        # If no range header, serve entire file
        app.logger.info('Serving complete file')
        
        # Read file in chunks
        def generate():
            with open(video_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        
        headers['Content-Length'] = str(file_size)
        
        return Response(
            generate(),
            200,
            mimetype='video/mp4',
            direct_passthrough=True,
            headers=headers
        )
        
    except Exception as e:
        app.logger.error(f'Error serving upload: {str(e)}')
        return f'Error: {str(e)}', 500

@app.route('/save_config', methods=['POST'])
def save_config():
    try:
        data = request.get_json()
        videos = data.get('videos', [])
        config_file = os.path.join(static_dir, 'video_config.json')
        with open(config_file, 'w') as f:
            json.dump(videos, f, indent=4)
        app.logger.info(f'Saved {len(videos)} videos to config')
        return jsonify({'success': True}), 200
    except Exception as e:
        app.logger.error(f'Error saving config: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(static_dir, 'favicon.ico', mimetype='image/x-icon')

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {error}')
    return 'Page not found. Available routes: /, /config, /playback, /stats', 404

@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f'An error occurred: {error}')
    return jsonify({'error': str(error)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)