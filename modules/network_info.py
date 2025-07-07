import socket
import psutil
import platform
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logging
from utils.platform_utils import get_os, run_command

class NetworkInfoCollector:
    """Class to collect and store network information."""
    
    def __init__(self):
        self.info_file = Path(__file__).parent.parent / 'data' / 'network_info.txt'
        self.info_file.parent.mkdir(exist_ok=True)
        self.logger = setup_logging('network_info')
        
    def collect_info(self):
        """Collect all network information and return as formatted string."""
        try:
            info = []
            info.append(f"=== Network Information - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            
            # System info
            info.append("\n[System Information]")
            info.append(f"Hostname: {socket.gethostname()}")
            info.append(f"OS: {platform.system()} {platform.release()}")
            
            # IP addresses
            info.append("\n[IP Addresses]")
            info.extend(self.get_ip_addresses())
            
            # Network interfaces
            info.append("\n[Network Interfaces]")
            info.extend(self.get_network_interfaces())
            
            # Network stats
            info.append("\n[Network Statistics]")
            info.extend(self.get_network_stats())
            
            # DNS info
            info.append("\n[DNS Information]")
            info.extend(self.get_dns_info())
            
            # Routing table
            info.append("\n[Routing Table]")
            info.extend(self.get_routing_table())
            
            # Save to file
            info_str = '\n'.join(info)
            self.save_to_file(info_str)
            
            return info_str
        except Exception as e:
            self.logger.error(f"Error collecting network info: {e}")
            raise

    def get_ip_addresses(self):
        """Get all IP addresses of the machine."""
        try:
            info = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        info.append(f"{interface}: {addr.address} (Netmask: {addr.netmask})")
            return info if info else ["No IPv4 addresses found"]
        except Exception as e:
            self.logger.error(f"Error getting IP addresses: {e}")
            return [f"Error: {str(e)}"]

    def get_network_interfaces(self):
        """Get detailed network interface information."""
        try:
            info = []
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface, addrs in psutil.net_if_addrs().items():
                info.append(f"\nInterface: {interface}")
                
                # Addresses
                for addr in addrs:
                    info.append(f"  {addr.family.name}: {addr.address}")
                    if addr.netmask:
                        info.append(f"    Netmask: {addr.netmask}")
                    if addr.broadcast:
                        info.append(f"    Broadcast: {addr.broadcast}")
                
                # Stats
                if interface in stats:
                    stat = stats[interface]
                    info.append(f"  Stats:")
                    info.append(f"    Up: {'Yes' if stat.isup else 'No'}")
                    info.append(f"    Speed: {stat.speed}Mbps")
                    info.append(f"    MTU: {stat.mtu}")
                
                # IO Counters
                if interface in io_counters:
                    io = io_counters[interface]
                    info.append(f"  Traffic:")
                    info.append(f"    Bytes Sent: {io.bytes_sent}")
                    info.append(f"    Bytes Recv: {io.bytes_recv}")
                    info.append(f"    Packets Sent: {io.packets_sent}")
                    info.append(f"    Packets Recv: {io.packets_recv}")
            
            return info if info else ["No network interfaces found"]
        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {e}")
            return [f"Error: {str(e)}"]

    def get_network_stats(self):
        """Get network statistics."""
        try:
            info = []
            net_io = psutil.net_io_counters()
            info.append(f"Total Bytes Sent: {net_io.bytes_sent}")
            info.append(f"Total Bytes Received: {net_io.bytes_recv}")
            info.append(f"Total Packets Sent: {net_io.packets_sent}")
            info.append(f"Total Packets Received: {net_io.packets_recv}")
            return info
        except Exception as e:
            self.logger.error(f"Error getting network stats: {e}")
            return [f"Error: {str(e)}"]

    def get_dns_info(self):
        """Get DNS information."""
        try:
            info = []
            if get_os() == 'windows':
                result = run_command(['ipconfig', '/all'])
                dns_lines = [line for line in result[0].split('\n') if 'DNS Servers' in line]
                info.extend(dns_lines if dns_lines else ["No DNS servers found in ipconfig"])
            else:
                result = run_command(['cat', '/etc/resolv.conf'])
                dns_lines = [line for line in result[0].split('\n') if line.startswith('nameserver')]
                info.extend(dns_lines if dns_lines else ["No nameservers found in /etc/resolv.conf"])
            return info
        except Exception as e:
            self.logger.error(f"Error getting DNS info: {e}")
            return [f"Error: {str(e)}"]

    def get_routing_table(self):
        """Get routing table information."""
        try:
            if get_os() == 'windows':
                result = run_command(['route', 'print'])
                return result[0].split('\n')
            else:
                result = run_command(['netstat', '-rn'])
                return result[0].split('\n')
        except Exception as e:
            self.logger.error(f"Error getting routing table: {e}")
            return [f"Error: {str(e)}"]

    def save_to_file(self, data):
        """Save network info to file."""
        try:
            with open(self.info_file, 'w', encoding='utf-8') as f:
                f.write(data)
        except Exception as e:
            self.logger.error(f"Error saving network info: {e}")
            raise