import socket
import subprocess
from typing import List, Dict, Optional, Tuple
from utils.logger import setup_logging
from utils.platform_utils import get_os, run_command, is_admin
import psutil

class PortController:
    """Class to manage network ports across different platforms."""
    
    def __init__(self):
        self.logger = setup_logging('port_control')
        
    def open_port(self, port: int) -> str:
        """Open a network port."""
        if not is_admin():
            return "Error: Run application as Administrator to open ports"
            
        try:
            if get_os() == 'windows':
                # Windows firewall rule
                result = run_command([
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name=Open_Port_{port}', 'dir=in', 'action=allow',
                    'protocol=TCP', f'localport={port}'
                ])
                if result[2] == 0:
                    return f"Port {port} opened in Windows firewall"
                return f"Error opening port: {result[1]}"
            else:
                # Linux iptables rule
                result = run_command([
                    'sudo', 'iptables', '-A', 'INPUT', '-p', 'tcp',
                    '--dport', str(port), '-j', 'ACCEPT'
                ])
                if result[2] == 0:
                    return f"Port {port} opened in iptables"
                return f"Error opening port: {result[1]}"
        except Exception as e:
            self.logger.error(f"Error opening port {port}: {e}")
            return f"Error opening port: {str(e)}"

    # ... (keep other methods the same) ...
        
    def is_port_open(self, port: int) -> bool:
        """Check if a port is open locally."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                return s.connect_ex(('localhost', port)) == 0
        except Exception as e:
            self.logger.error(f"Error checking port {port}: {e}")
            raise

    def check_port(self, port: int) -> str:
        """Check the status of a specific port."""
        try:
            if self.is_port_open(port):
                return f"Port {port} is open"
            return f"Port {port} is closed"
        except Exception as e:
            return f"Error checking port {port}: {str(e)}"

   

    def close_port(self, port: int) -> str:
        """Close a network port."""
        if not is_admin():
            return "Error: Administrator/root privileges required to close ports"
            
        try:
            if get_os() == 'windows':
                result = run_command([
                    'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                    f'name=Open Port {port}'
                ])
                if result[2] == 0:
                    return f"Port {port} closed in Windows firewall"
                return f"Error closing port: {result[1]}"
            else:
                result = run_command([
                    'iptables', '-D', 'INPUT', '-p', 'tcp',
                    '--dport', str(port), '-j', 'ACCEPT'
                ])
                if result[2] == 0:
                    return f"Port {port} closed in iptables"
                return f"Error closing port: {result[1]}"
        except Exception as e:
            self.logger.error(f"Error closing port {port}: {e}")
            return f"Error closing port: {str(e)}"

    def get_port_process(self, port: int) -> Optional[Dict[str, str]]:
        """Get process information for a specific port."""
        try:
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port == port:
                    try:
                        proc = psutil.Process(conn.pid)
                        return {
                            'pid': conn.pid,
                            'name': proc.name(),
                            'status': proc.status(),
                            'port': port
                        }
                    except psutil.NoSuchProcess:
                        return None
            return None
        except Exception as e:
            self.logger.error(f"Error getting process for port {port}: {e}")
            raise

    def get_open_ports(self) -> List[Dict[str, str]]:
        """Get a list of all open ports."""
        try:
            open_ports = []
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN' and conn.laddr:
                    port_info = {
                        'port': conn.laddr.port,
                        'address': conn.laddr.ip,
                        'type': conn.type.name,
                        'status': conn.status
                    }
                    
                    try:
                        proc = psutil.Process(conn.pid)
                        port_info.update({
                            'pid': conn.pid,
                            'process': proc.name(),
                            'cmdline': ' '.join(proc.cmdline())
                        })
                    except psutil.NoSuchProcess:
                        port_info['process'] = 'Unknown'
                        
                    open_ports.append(port_info)
                    
            return open_ports
        except Exception as e:
            self.logger.error(f"Error getting open ports: {e}")
            raise

    def get_status(self) -> str:
        """Get status of common ports."""
        try:
            status = []
            common_ports = [21, 22, 80, 443, 3306, 5432]  # FTP, SSH, HTTP, HTTPS, MySQL, PostgreSQL
            
            for port in common_ports:
                port_info = self.check_port(port)
                process_info = self.get_port_process(port)
                
                if process_info:
                    status.append(f"Port {port}: {port_info} (Process: {process_info['name']} PID: {process_info['pid']})")
                else:
                    status.append(f"Port {port}: {port_info}")
                    
            return "\n".join(status)
        except Exception as e:
            self.logger.error(f"Error getting ports status: {e}")
            return f"Error getting ports status: {str(e)}"