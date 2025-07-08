#!/usr/bin/env python3
import paramiko
import time
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('remote_test.log')
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
    
    def execute_command(self, command, sudo=False, timeout=60):
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
    
    def run_tests(self):
        """Run the test workflow on the remote server"""
        if not self.connect():
            return False
        
        try:
            # 1. Create remote directory
            self.execute_command(f'mkdir -p {self.remote_path}')
            
            # 2. Upload test files
            test_files = ['test_flow.py', 'test_config.json']
            for f in test_files:
                local_path = Path(f).absolute()
                if local_path.exists():
                    self.upload_file(str(local_path))
                else:
                    logger.warning(f"Local file not found: {local_path}")
            
            # 3. Install dependencies
            self.execute_command('pip install paramiko', sudo=True)
            
            # 4. Install test dependencies
            self.execute_command('pip install mininet ryu scapy pandas', sudo=True)
            
            # 5. Upload the test script
            self.upload_file('remote_test.sh', str(self.remote_path / 'remote_test.sh'))
            
            # 6. Make the script executable
            self.execute_command(f'chmod +x {self.remote_path}/remote_test.sh')
            
            # 7. Run the test script
            exit_status, output, error = self.execute_command(
                f'cd {self.remote_path} && ./remote_test.sh',
                sudo=False,
                timeout=1800  # 30 minutes timeout
            )
            
            # 5. Download results
            output_files = [
                'test_traffic.pcap',
                'test_features.csv',
                'test_flow_features.csv',
                'test_timeline.csv',
                'test_flow.log'
            ]
            
            for f in output_files:
                remote_file = self.remote_path / f
                local_file = Path(f).absolute()
                try:
                    self.sftp.get(str(remote_file), str(local_file))
                    logger.info(f"Downloaded {remote_file} to {local_file}")
                except Exception as e:
                    logger.warning(f"Failed to download {remote_file}: {str(e)}")
            
            return exit_status == 0
            
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
    
    if runner.run_tests():
        logger.info("✅ Remote tests completed successfully!")
        return 0
    else:
        logger.error("❌ Remote tests failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
