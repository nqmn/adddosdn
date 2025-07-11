import time
import logging
import subprocess
from pathlib import Path
from scapy.all import Ether, IP, TCP, UDP, Raw, RandShort, sendp

# Configure a dedicated logger for benign traffic details
benign_logger = logging.getLogger('benign_logger')
benign_logger.setLevel(logging.DEBUG)
benign_logger.propagate = False # Prevent messages from being passed to the root logger



def run_benign_traffic(net, duration, output_dir, host_ips):
    """
    Generates various types of benign traffic (ICMP, TCP, UDP, Telnet, SSH, FTP, HTTP)
    between h3 and h5 in the Mininet network.
    """
    # Ensure output directory exists before setting up file handlers
    Path(output_dir).mkdir(exist_ok=True)

    # File handler for benign.log
    benign_log_file_handler = logging.FileHandler(Path(output_dir) / 'benign.log')
    benign_log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    benign_logger.addHandler(benign_log_file_handler)

    # Console handler for benign_logger
    benign_console_handler = logging.StreamHandler()
    benign_console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    benign_console_handler.setLevel(logging.INFO) # Set to INFO for console output
    benign_logger.addHandler(benign_console_handler)

    benign_logger.info(f"Starting benign traffic for {duration} seconds...")
    h3 = net.get('h3')
    h5 = net.get('h5')
    h3_ip = host_ips["h3"]
    h5_ip = host_ips["h5"]
    h3_intf = h3.intfNames()[0] # Get the interface name of h3
    end_time = time.time() + duration
    
    traffic_count = 0
    while time.time() < end_time:
        # ICMP traffic (using Mininet's ping command)
        h3.cmd(f'ping -c 1 {h5_ip} > /dev/null')
        h5.cmd(f'ping -c 1 {h3_ip} > /dev/null')
        benign_logger.debug(f"Generated ICMP traffic {traffic_count}")

        # Scapy commands to be executed within h3's namespace
        scapy_base_cmd = "from scapy.all import Ether, IP, TCP, UDP, Raw, RandShort, sendp;"

        # TCP traffic (h3 to h5, port 12345)
        tcp_scapy_cmd = f"tcp_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=12345, flags='PA')/Raw(load='TCP benign traffic {traffic_count}'); sendp(tcp_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{tcp_scapy_cmd}"')
        benign_logger.debug(f"Generated TCP traffic {traffic_count}")

        # UDP traffic (h3 to h5, port 12346)
        udp_scapy_cmd = f"udp_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/UDP(sport=RandShort(), dport=12346)/Raw(load='UDP benign traffic {traffic_count}'); sendp(udp_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{udp_scapy_cmd}"')
        benign_logger.debug(f"Generated UDP traffic {traffic_count}")

        # Telnet traffic (h3 to h5, port 23)
        telnet_scapy_cmd = f"telnet_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=23, flags='PA')/Raw(load='Telnet benign traffic {traffic_count}'); sendp(telnet_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{telnet_scapy_cmd}"')
        benign_logger.debug(f"Generated Telnet traffic {traffic_count}")

        # SSH traffic (h3 to h5, port 22)
        ssh_scapy_cmd = f"ssh_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=22, flags='PA')/Raw(load='SSH benign traffic {traffic_count}'); sendp(ssh_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{ssh_scapy_cmd}"')
        benign_logger.debug(f"Generated SSH traffic {traffic_count}")

        # FTP traffic (h3 to h5, port 21)
        ftp_scapy_cmd = f"ftp_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=21, flags='PA')/Raw(load='FTP benign traffic {traffic_count}'); sendp(ftp_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{ftp_scapy_cmd}"')
        benign_logger.debug(f"Generated FTP traffic {traffic_count}")

        # HTTP traffic (h3 to h5, port 80)
        http_scapy_cmd = f"http_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=80, flags='PA')/Raw(load=b'GET / HTTP/1.1\nHost: {h5_ip}\nUser-Agent: ScapyBenignTraffic\nConnection: close\n\n'); sendp(http_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{http_scapy_cmd}"')
        benign_logger.debug(f"Generated HTTP traffic {traffic_count}")
        
        traffic_count += 1
        time.sleep(1) # Send traffic every second
    
    benign_logger.info("Benign traffic finished.")
