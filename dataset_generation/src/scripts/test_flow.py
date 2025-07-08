#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import signal
import json
import logging
import ctypes
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_flow.log')
    ]
)
logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_config = self.project_root / 'test_config.json'
        self.output_files = [
            'test_traffic.pcap',
            'test_features.csv',
            'test_flow_features.csv',
            'test_timeline.csv'
        ]
        self.processes = []
        
    def cleanup(self):
        """Remove any existing output files"""
        logger.info("Cleaning up old test files...")
        for f in self.output_files:
            file_path = self.project_root / f
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Removed {file_path}")
    
    def check_dependencies(self):
        """Verify required dependencies are installed"""
        logger.info("Checking dependencies...")
        required = ['mininet', 'ryu-manager', 'scapy', 'pandas']
        missing = []
        
        for dep in required:
            try:
                __import__(dep)
                logger.info(f"✓ {dep}")
            except ImportError:
                missing.append(dep)
                logger.error(f"✗ {dep} not found")
        
        if missing:
            logger.error("Missing required dependencies. Please install them using:")
            logger.error("pip install " + " ".join(missing))
            return False
        return True
    
    def run_test(self):
        """Run the test flow"""
        logger.info("="*50)
        logger.info("Starting test flow...")
        logger.info("="*50)
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Python version: {sys.version}")
        
        # Log environment variables
        logger.info("Environment variables:")
        for key, value in os.environ.items():
            if any(x in key.lower() for x in ['path', 'python', 'home', 'user']):
                logger.info(f"  {key}: {value}")
        
        # Log directory contents
        logger.info("Current directory contents:")
        try:
            for item in os.listdir('.'):
                logger.info(f"  {item}")
        except Exception as e:
            logger.error(f"Failed to list directory contents: {str(e)}")
            
        # Check for required files
        required_files = [
            'main.py',
            'config.json',
            'controller/ryu_controller_app.py',
            'topology.py'
        ]
        
        for file in required_files:
            path = self.project_root / file
            if not path.exists():
                logger.error(f"Required file not found: {path}")
                return False
            logger.info(f"Found required file: {path}")
        
        # 1. Start Ryu controller
        logger.info("Starting Ryu controller...")
        try:
            ryu_cmd = [
                'ryu-manager',
                '--ofp-tcp-listen-port', '6633',
                '--wsapi-port', '8080',
                str(self.project_root / 'controller' / 'ryu_controller_app.py')
            ]
            ryu_proc = subprocess.Popen(
                ryu_cmd,
                stdout=open('ryu_controller.log', 'w'),
                stderr=subprocess.STDOUT
            )
            self.processes.append(ryu_proc)
            logger.info(f"Ryu controller started (PID: {ryu_proc.pid})")
            
            # Give controller time to start
            time.sleep(5)
            
            # Verify controller is running
            if ryu_proc.poll() is not None:
                logger.error("Ryu controller failed to start")
                with open('ryu_controller.log', 'r') as f:
                    logger.error(f"Ryu controller logs:\n{f.read()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Ryu controller: {str(e)}")
            return False
        
        try:
            # 2. Run main.py with test config
            logger.info("Starting dataset generation...")
            main_cmd = [
                'sudo', '-E', 'python3', 'main.py',
                str(self.test_config)
            ]
            
            logger.info(f"Running: {' '.join(main_cmd)}")
            main_proc = subprocess.Popen(
                main_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output
            for line in main_proc.stdout:
                logger.info(line.strip())
            
            # Wait for completion
            main_proc.wait()
            
            if main_proc.returncode != 0:
                logger.error(f"main.py failed with return code {main_proc.returncode}")
                logger.error(main_proc.stderr.read())
                return False
                
            # 3. Verify output files were created
            logger.info("Verifying output files...")
            missing_files = []
            for f in self.output_files:
                file_path = self.project_root / f
                if not file_path.exists():
                    missing_files.append(f)
                    logger.error(f"Missing output file: {f}")
                else:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    logger.info(f"✓ {f} - {size_mb:.2f} MB")
            
            if missing_files:
                logger.error("Test failed: Some output files are missing")
                return False
                
            logger.info("✓ All output files created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}", exc_info=True)
            return False
            
        finally:
            # Cleanup processes
            self.cleanup_processes()
    
    def cleanup_processes(self):
        """Terminate any running processes"""
        logger.info("Cleaning up processes...")
        for proc in self.processes:
            try:
                if proc.poll() is None:  # Process is still running
                    logger.info(f"Terminating process {proc.pid}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
            except Exception as e:
                logger.error(f"Error terminating process {proc.pid}: {str(e)}")

def is_admin():
    """Check if the current user has admin privileges on Windows"""
    try:
        return os.name == 'nt' and ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def main():
    # Check for admin/root privileges
    if os.name == 'posix':
        if os.geteuid() != 0:
            logger.error("This script must be run with sudo privileges on Unix-like systems.")
            return 1
    elif os.name == 'nt' and not is_admin():
        logger.error("This script must be run as Administrator on Windows.")
        return 1
    
    runner = TestRunner()
    runner.cleanup()
    
    if not runner.check_dependencies():
        return 1
    
    success = runner.run_test()
    
    if success:
        logger.info("✅ Test completed successfully!")
        return 0
    else:
        logger.error("❌ Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
