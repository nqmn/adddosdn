#!/usr/bin/env python3
import paramiko
import os
import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('remote_test_run.log')
    ]
)
logger = logging.getLogger(__name__)

class RemoteTestRunner:
    def __init__(self, hostname, port, username, password, remote_path):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.remote_path = Path(remote_path)
        self.ssh = None
        self.sftp = None
    
    def connect(self):
        """Establish SSH connection"""
        try:
            logger.info(f"Connecting to {self.username}@{self.hostname}:{self.port}")
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
                banner_timeout=60,
                auth_timeout=30
            )
            
            self.sftp = self.ssh.open_sftp()
            logger.info("SSH connection established")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
    
    def execute_command(self, command, sudo=False, timeout=30):
        """Execute a command on the remote host"""
        try:
            if sudo:
                command = f'echo {self.password} | sudo -S {command}'
            
            logger.info(f"Executing: {command}")
            
            stdin, stdout, stderr = self.ssh.exec_command(
                command,
                get_pty=True,
                timeout=timeout
            )
            
            # Wait for command to complete
            exit_status = stdout.channel.recv_exit_status()
            
            # Get output
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if output:
                logger.info(f"Output: {output}")
            if error:
                logger.error(f"Error: {error}")
                
            return exit_status, output, error
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return -1, "", str(e)
    
    def upload_file(self, local_path, remote_path=None):
        """Upload a file to the remote server"""
        try:
            if remote_path is None:
                remote_path = self.remote_path / os.path.basename(local_path)
            
            logger.info(f"Uploading {local_path} to {remote_path}")
            self.sftp.put(local_path, str(remote_path))
            return True
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            return False
    
    def run_test(self):
        """Run the test on the remote server"""
        if not self.connect():
            return False
        
        try:
            # 1. Create remote directory
            self.execute_command(f'mkdir -p {self.remote_path}')
            
            # 2. Upload test files
            test_files = [
                'simple_test.py',
                'main.py',
                'config.json',
                'topology.py',
                'controller/ryu_controller_app.py',
                'attacks/gen_syn_flood.py',
                'attacks/gen_udp_flood.py',
                'attacks/gen_advanced_adversarial_ddos_attacks.py'
            ]
            
            # First, create all necessary directories
            dirs = set()
            for file in test_files:
                dir_path = os.path.dirname(file)
                if dir_path and dir_path not in dirs:
                    remote_dir = str(self.remote_path / dir_path).replace('\\', '/')
                    self.execute_command(f'mkdir -p {remote_dir}')
                    dirs.add(dir_path)
            
            # Then upload files
            for file in test_files:
                local_path = Path(file)
                if local_path.exists():
                    remote_file = str(self.remote_path / file).replace('\\', '/')
                    self.upload_file(str(local_path), remote_file)
                    logger.info(f"Uploaded {local_path} to {remote_file}")
                else:
                    logger.warning(f"Local file not found: {local_path}")
            
            # 3. Run the simple test to check environment
            logger.info("Running environment check...")
            remote_path = str(self.remote_path).replace('\\', '/')
            exit_status, output, error = self.execute_command(
                f'cd {remote_path} && python3 simple_test.py',
                timeout=60
            )
            
            if exit_status != 0:
                logger.error("Environment check failed")
                return False
            
            # 4. Install dependencies
            logger.info("Installing dependencies...")
            self.execute_command(
                'pip3 install mininet ryu scapy pandas',
                sudo=True,
                timeout=300
            )
            
            # Ensure the test config exists
            self.execute_command(
                f'cd {remote_path} && ls -la',
                timeout=30
            )
            
            # 5. Run the test
            logger.info("Starting test...")
            exit_status, output, error = self.execute_command(
                f'cd {remote_path} && sudo python3 main.py test_config.json',
                timeout=600  # 10 minutes timeout
            )
            
            # 6. Check results
            if exit_status == 0:
                logger.info("Test completed successfully")
                
                # Download results
                result_files = [
                    'test_traffic.pcap',
                    'test_features.csv',
                    'test_flow_features.csv',
                    'test_timeline.csv'
                ]
                
                for file in result_files:
                    remote_file = f"{remote_path}/{file}"
                    local_file = Path(file)
                    try:
                        self.sftp.get(str(remote_file), str(local_file))
                        logger.info(f"Downloaded {remote_file} to {local_file}")
                    except Exception as e:
                        logger.warning(f"Failed to download {remote_file}: {str(e)}")
                
                return True
            else:
                logger.error(f"Test failed with exit code {exit_status}")
                logger.error(f"Error output: {error}")
                return False
            
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            return False
            
        finally:
            self.ssh.close()

def main():
    # Configuration
    config = {
        'hostname': 'jtmksrv',
        'port': 656,
        'username': 'user',
        'password': '1',
        'remote_path': '/home/user/dataset/test_run'
    }
    
    logger.info("Starting remote test execution...")
    runner = RemoteTestRunner(**config)
    
    if runner.run_test():
        logger.info("✅ Remote test completed successfully!")
        return 0
    else:
        logger.error("❌ Remote test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
