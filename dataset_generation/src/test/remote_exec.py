#!/usr/bin/env python3
import paramiko
import argparse
import getpass
import sys
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('remote_exec.log')
    ]
)
logger = logging.getLogger(__name__)

class RemoteCLI:
    def __init__(self, hostname, port, username, password=None, key_filename=None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.ssh = None
        self.sftp = None

    def connect(self):
        """Establish SSH connection"""
        try:
            logger.info(f"Connecting to {self.username}@{self.hostname}:{self.port}")
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_args = {
                'hostname': self.hostname,
                'port': self.port,
                'username': self.username,
                'timeout': 10,
                'banner_timeout': 60,
                'auth_timeout': 30
            }
            
            if self.password:
                logger.debug("Using password authentication")
                connect_args['password'] = self.password
            if self.key_filename:
                logger.debug(f"Using SSH key from {self.key_filename}")
                connect_args['key_filename'] = self.key_filename
            
            logger.debug(f"Connection args: { {k: '***' if k == 'password' else v for k, v in connect_args.items()} }")
            self.ssh.connect(**connect_args)
            logger.info("SSH connection established")
            
            logger.debug("Opening SFTP session")
            self.sftp = self.ssh.open_sftp()
            logger.info("SFTP session started")
            
            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}", exc_info=True)
            return False

    def execute_command(self, command, sudo=False, get_pty=False, timeout=30):
        """Execute a command on the remote host with a timeout"""
        if not self.ssh:
            print("Not connected. Call connect() first.")
            return None, None, None

        try:
            channel = self.ssh.get_transport().open_session()
            channel.get_pty()
            channel.settimeout(timeout)
            
            if sudo:
                command = f'sudo -S -p "" {command}'
            
            channel.exec_command(command)
            
            if sudo and self.password:
                channel.send(f"{self.password}\n")
            
            output = ""
            error = ""
            
            while not channel.exit_status_ready():
                if channel.recv_ready():
                    output += channel.recv(1024).decode('utf-8')
                if channel.recv_stderr_ready():
                    error += channel.recv_stderr(1024).decode('utf-8')
                time.sleep(0.1)
            
            # Get any remaining output
            while channel.recv_ready():
                output += channel.recv(1024).decode('utf-8')
            while channel.recv_stderr_ready():
                error += channel.recv_stderr(1024).decode('utf-8')
            
            exit_status = channel.recv_exit_status()
            channel.close()
            
            return output.strip(), error.strip(), exit_status
            
        except Exception as e:
            return None, str(e), 1
            
    def execute_mininet_command(self, command, timeout=60):
        """Execute a Mininet command with proper sudo handling"""
        if not self.ssh:
            logger.error("Not connected. Call connect() first.")
            return None, None, None
            
        try:
            logger.info(f"Executing Mininet command: {command}")
            
            # Create a temporary script to run the command
            script_content = f'''#!/bin/bash
            # Set the password variable
            export SUDO_ASKPASS=/bin/false
            
            # Function to handle the command execution
            run_command() {{
                echo {self.password} | sudo -S {command}
                return $?
            }}
            
            # Run the command with a timeout
            run_command
            exit $?
            '''
            
            # Create a temporary file for the script
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                # Make the script executable
                self.sftp.chmod(script_path, 0o700)
                
                # Execute the script
                stdin, stdout, stderr = self.ssh.exec_command(f'bash {script_path}')
                
                # Set a timeout for the command
                start_time = time.time()
                output = ""
                error = ""
                
                while True:
                    # Read from stdout
                    if stdout.channel.recv_ready():
                        output += stdout.channel.recv(4096).decode('utf-8', 'ignore')
                    
                    # Read from stderr
                    if stdout.channel.recv_stderr_ready():
                        error += stdout.channel.recv_stderr(4096).decode('utf-8', 'ignore')
                    
                    # Check if command has completed
                    if stdout.channel.exit_status_ready():
                        exit_status = stdout.channel.recv_exit_status()
                        break
                    
                    # Check for timeout
                    if time.time() - start_time > timeout:
                        logger.warning(f"Command timed out after {timeout} seconds")
                        exit_status = -1
                        break
                    
                    time.sleep(0.1)
                
                # Get any remaining output
                output += stdout.read().decode('utf-8', 'ignore')
                error += stderr.read().decode('utf-8', 'ignore')
                
                logger.info(f"Command completed with status: {exit_status}")
                logger.debug(f"Output: {output[:200]}...")
                
                return output, error, exit_status
                
            finally:
                # Clean up the temporary file
                try:
                    self.ssh.exec_command(f'rm -f {script_path}')
                except:
                    pass
                
                try:
                    os.unlink(script_path)
                except:
                    pass
            
        except Exception as e:
            return None, str(e), 1

    def upload_file(self, local_path, remote_path):
        """Upload a file to the remote host"""
        try:
            self.sftp.put(local_path, remote_path)
            return True, None
        except Exception as e:
            return False, str(e)

    def download_file(self, remote_path, local_path):
        """Download a file from the remote host"""
        try:
            self.sftp.get(remote_path, local_path)
            return True, None
        except Exception as e:
            return False, str(e)

    def close(self):
        """Close the SSH connection"""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()

def interactive_shell(remote_cli):
    """Start an interactive shell session"""
    print("Starting interactive shell. Type 'exit' or 'quit' to end the session.")
    while True:
        try:
            command = input(f"{remote_cli.username}@{remote_cli.hostname}$ ").strip()
            if not command:
                continue
            if command.lower() in ['exit', 'quit']:
                break
                
            output, error, exit_code = remote_cli.execute_command(
                command, 
                sudo=command.startswith('sudo'),
                get_pty=True
            )
            
            if output:
                print("--- Output ---")
                print(output)
            if error:
                print("--- Errors ---")
                print(error)
            print(f"Exit code: {exit_code}")
            
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'quit' to end the session")
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Remote CLI Tool')
    parser.add_argument('--host', required=True, help='Remote host')
    parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('--user', required=True, help='SSH username')
    parser.add_argument('--password', default='1', help='SSH password (default: 1)')
    parser.add_argument('--key', help='Path to SSH private key')
    parser.add_argument('--command', help='Single command to execute (optional)')
    parser.add_argument('--mininet', action='store_true',
                       help='Run the command as a Mininet command')
    parser.add_argument('--upload', nargs=2, metavar=('LOCAL', 'REMOTE'), 
                       help='Upload a file to the remote host')
    parser.add_argument('--download', nargs=2, metavar=('REMOTE', 'LOCAL'),
                       help='Download a file from the remote host')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Command execution timeout in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # Get password if not provided and needed
    password = args.password
    if not password and not args.key:
        password = getpass.getpass("Enter SSH password: ")
    
    # Create remote CLI instance
    remote = RemoteCLI(
        hostname=args.host,
        port=args.port,
        username=args.user,
        password=password,
        key_filename=args.key
    )
    
    try:
        # Connect to the remote host
        if not remote.connect():
            print("Failed to connect to the remote host")
            return 1
        
        # Handle file upload
        if args.upload:
            success, error = remote.upload_file(args.upload[0], args.upload[1])
            if success:
                print(f"File uploaded successfully to {args.upload[1]}")
            else:
                print(f"Upload failed: {error}")
            return 0
        
        # Handle file download
        if args.download:
            success, error = remote.download_file(args.download[0], args.download[1])
            if success:
                print(f"File downloaded successfully to {args.download[1]}")
            else:
                print(f"Download failed: {error}")
            return 0
        
        # Execute single command or start interactive shell
        if args.command:
            if args.mininet:
                output, error, exit_code = remote.execute_mininet_command(
                    args.command,
                    timeout=args.timeout
                )
            else:
                output, error, exit_code = remote.execute_command(
                    args.command, 
                    sudo=args.command.startswith('sudo'),
                    get_pty=True,
                    timeout=args.timeout
                )
            
            if output:
                print("--- Output ---")
                print(output)
            if error:
                print("--- Errors ---")
                print(error)
            print(f"Exit code: {exit_code}")
        else:
            interactive_shell(remote)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        remote.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
