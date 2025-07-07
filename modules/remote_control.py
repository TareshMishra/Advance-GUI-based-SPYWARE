from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from threading import Lock
from pathlib import Path
from utils.logger import setup_logging
from utils.platform_utils import run_command
import subprocess
import platform
import json
import time

class RemoteControlServer:
    """Remote control server using Flask and WebSockets."""
    
    def __init__(self):
        self.app = Flask(__name__, 
                        template_folder=str(Path(__file__).parent.parent / 'templates'),
                        static_folder=str(Path(__file__).parent.parent / 'static'))
        self.socketio = SocketIO(self.app)
        self.thread = None
        self.thread_lock = Lock()
        self.clients = 0
        self.logger = setup_logging('remote_control')
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes."""
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/command', methods=['POST'])
        def execute_command():
            try:
                data = request.json
                command = data.get('command')
                if not command:
                    return jsonify({'error': 'No command provided'}), 400
                    
                result = self.run_command(command)
                return jsonify({'result': result})
            except Exception as e:
                self.logger.error(f"Error executing command via HTTP: {e}")
                return jsonify({'error': str(e)}), 500

        @self.socketio.on('connect')
        def handle_connect():
            with self.thread_lock:
                self.clients += 1
                self.logger.info(f"Client connected. Total clients: {self.clients}")
            self.socketio.emit('response', {'data': 'Connected to server'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            with self.thread_lock:
                self.clients -= 1
                self.logger.info(f"Client disconnected. Total clients: {self.clients}")

        @self.socketio.on('command')
        def handle_command(data):
            try:
                command = data.get('command')
                if not command:
                    self.logger.warning("Received empty command via WebSocket")
                    self.socketio.emit('response', {'error': 'No command provided'})
                    return
                    
                self.logger.info(f"Executing command via WebSocket: {command}")
                result = self.run_command(command)
                self.socketio.emit('response', {'result': result})
            except Exception as e:
                self.logger.error(f"Error executing command via WebSocket: {e}")
                self.socketio.emit('response', {'error': str(e)})

    def run_command(self, command):
        """Run a system command and return the output."""
        try:
            # Handle special commands
            if command.lower() == 'get_system_info':
                return self.get_system_info()
                
            # Run the command
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    executable='/bin/bash'
                )
                
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.warning(f"Command failed: {command}. Error: {stderr}")
                return f"Error: {stderr}"
                
            self.logger.info(f"Command executed successfully: {command}")
            return stdout if stdout else "Command executed successfully (no output)"
        except Exception as e:
            self.logger.error(f"Error running command {command}: {e}")
            raise

    def get_system_info(self):
        """Get system information."""
        try:
            info = {
                'system': platform.system(),
                'node': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
            return json.dumps(info, indent=2)
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            raise

    def start(self, host='0.0.0.0', port=5000):
        """Start the remote control server."""
        if not self.thread or not self.thread.is_alive():
            self.thread = self.socketio.start_background_task(
                target=self.socketio.run,
                app=self.app,
                host=host,
                port=port,
                debug=False,
                use_reloader=False
            )
            self.logger.info(f"Remote control server started on {host}:{port}")

    # ... (previous code remains the same) ...

    def stop(self):
        """Stop the remote control server."""
        try:
            if hasattr(self, 'socketio') and self.socketio:
                self.socketio.stop()
            self.logger.info("Remote control server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")

    def is_running(self):
        """Check if the server is running."""
        return self.thread is not None and self.thread.is_alive()

    def get_connection_info(self):
        """Get connection information."""
        return f"Remote control server running: {self.is_running()}\n" \
               f"Connected clients: {self.clients}\n" \
               f"Access at: http://localhost:5000"