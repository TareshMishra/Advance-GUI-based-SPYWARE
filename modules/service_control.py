import subprocess
import platform
from typing import List, Dict, Optional
from utils.logger import setup_logging
from utils.platform_utils import get_os, run_command, is_admin
import time

class ServiceController:
    """Class to manage system services across different platforms."""
    
    def __init__(self):
        self.logger = setup_logging('service_control')
        

    def start_service(self, service_name: str) -> str:
        """Start a system service."""
        if not is_admin():
            return "Error: Run application as Administrator to manage services"
            
        try:
            if get_os() == 'windows':
                result = run_command(['sc', 'start', service_name])
            else:
                result = run_command(['sudo', 'systemctl', 'start', service_name])
                
            if result[2] == 0:
                return f"Service '{service_name}' started successfully"
            return f"Error starting service: {result[1]}"
        except Exception as e:
            self.logger.error(f"Error starting service {service_name}: {e}")
            return f"Error starting service: {str(e)}"    
        
    def install_service(self, service_name: str) -> str:
        """Install a system service."""
        if not is_admin():
            return "Error: Administrator/root privileges required to install services"
            
        try:
            if get_os() == 'windows':
                result = run_command(['sc', 'create', service_name, 'binPath=', 'C:\\path\\to\\service.exe'])
                if result[2] == 0:
                    return f"Service '{service_name}' installed successfully"
                return f"Error installing service: {result[1]}"
            else:
                if service_name.lower() == 'mysql':
                    result = run_command(['apt-get', 'install', '-y', 'mysql-server'])
                elif service_name.lower() == 'apache2':
                    result = run_command(['apt-get', 'install', '-y', 'apache2'])
                else:
                    return f"Automatic installation not supported for service '{service_name}'"
                
                if result[2] == 0:
                    return f"Service '{service_name}' installed successfully"
                return f"Error installing service: {result[1]}"
        except Exception as e:
            self.logger.error(f"Error installing service {service_name}: {e}")
            return f"Error installing service: {str(e)}"

    

    def stop_service(self, service_name: str) -> str:
        """Stop a system service."""
        try:
            if get_os() == 'windows':
                result = run_command(['net', 'stop', service_name])
            else:
                result = run_command(['systemctl', 'stop', service_name])
                
            if result[2] == 0:
                return f"Service '{service_name}' stopped successfully"
            return f"Error stopping service: {result[1]}"
        except Exception as e:
            self.logger.error(f"Error stopping service {service_name}: {e}")
            return f"Error stopping service: {str(e)}"

    def restart_service(self, service_name: str) -> str:
        """Restart a system service."""
        try:
            if get_os() == 'windows':
                stop_result = run_command(['net', 'stop', service_name])
                if stop_result[2] != 0:
                    return f"Error stopping service: {stop_result[1]}"
                    
                time.sleep(2)
                
                start_result = run_command(['net', 'start', service_name])
                if start_result[2] != 0:
                    return f"Error starting service: {start_result[1]}"
                    
                return f"Service '{service_name}' restarted successfully"
            else:
                result = run_command(['systemctl', 'restart', service_name])
                if result[2] == 0:
                    return f"Service '{service_name}' restarted successfully"
                return f"Error restarting service: {result[1]}"
        except Exception as e:
            self.logger.error(f"Error restarting service {service_name}: {e}")
            return f"Error restarting service: {str(e)}"

    def get_service_status(self, service_name: str) -> str:
        """Get the status of a specific service."""
        try:
            if get_os() == 'windows':
                result = run_command(['sc', 'query', service_name])
                if "RUNNING" in result[0]:
                    return f"Service '{service_name}' is running"
                elif "STOPPED" in result[0]:
                    return f"Service '{service_name}' is stopped"
                else:
                    return result[0] or result[1] or f"Unknown status for service '{service_name}'"
            else:
                result = run_command(['systemctl', 'is-active', service_name])
                if result[2] == 0:
                    return f"Service '{service_name}' is running"
                else:
                    result = run_command(['systemctl', 'status', service_name])
                    if "inactive" in result[0].lower():
                        return f"Service '{service_name}' is stopped"
                    return result[0] or result[1] or f"Unknown status for service '{service_name}'"
        except Exception as e:
            self.logger.error(f"Error getting status for service {service_name}: {e}")
            return f"Error getting service status: {str(e)}"

    def get_status(self) -> str:
        """Get status of all services."""
        try:
            status = []
            common_services = ['mysql', 'apache2', 'ssh', 'postgresql'] if get_os() != 'windows' else [
                'MySQL', 'Apache2.4', 'Spooler', 'EventLog']
            
            for service in common_services:
                status.append(f"{service}: {self.get_service_status(service)}")
                
            return "\n".join(status)
        except Exception as e:
            self.logger.error(f"Error getting services status: {e}")
            return f"Error getting services status: {str(e)}"

    def list_services(self) -> List[Dict[str, str]]:
        """List all available services."""
        try:
            services = []
            if get_os() == 'windows':
                result = run_command(['sc', 'query', 'type=', 'service', 'state=', 'all'])
                if result[2] == 0:
                    lines = result[0].split('\n')
                    for line in lines:
                        if 'SERVICE_NAME:' in line:
                            service_name = line.split('SERVICE_NAME:')[1].strip()
                            status = self.get_service_status(service_name)
                            services.append({'name': service_name, 'status': status})
            else:
                result = run_command(['systemctl', 'list-units', '--type=service', '--all'])
                if result[2] == 0:
                    lines = result[0].split('\n')[1:-7]  # Skip header and footer
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            service_name = parts[0]
                            status = ' '.join(parts[3:])
                            services.append({'name': service_name, 'status': status})
            
            return services
        except Exception as e:
            self.logger.error(f"Error listing services: {e}")
            return [{'error': str(e)}]