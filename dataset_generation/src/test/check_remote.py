import paramiko
import os

def main():
    hostname = 'jtmksrv'
    port = 656
    username = 'user'
    password = '1'
    remote_path = '/home/user/dataset/test_run/'
    
    # Connect to the remote server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {username}@{hostname}:{port}...")
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # List files in the remote directory
        stdin, stdout, stderr = ssh.exec_command(f'ls -la {remote_path}')
        files = stdout.read().decode()
        print("\nRemote directory contents:")
        print(files)
        
        # Check for specific output files
        output_files = [
            'test_traffic.pcap',
            'test_features.csv',
            'test_flow_features.csv',
            'test_timeline.csv',
            '*.log'
        ]
        
        sftp = ssh.open_sftp()
        
        # Download output files
        print("\nDownloading output files:")
        for pattern in output_files:
            try:
                stdin, stdout, stderr = ssh.exec_command(f'ls {remote_path}/{pattern} 2>/dev/null')
                found_files = stdout.read().decode().split()
                
                for remote_file in found_files:
                    remote_file = remote_file.strip()
                    if remote_file:
                        local_file = os.path.basename(remote_file)
                        print(f"Downloading {remote_file} to {local_file}...")
                        sftp.get(remote_file, local_file)
                        print(f"Downloaded {remote_file} successfully.")
            except Exception as e:
                print(f"Error processing {pattern}: {str(e)}")
        
        # Check for any errors in the log files
        print("\nChecking log files:")
        stdin, stdout, stderr = ssh.exec_command(f'grep -r "ERROR\|Exception" {remote_path}/*.log 2>/dev/null || echo "No errors found in logs"')
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        ssh.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()
