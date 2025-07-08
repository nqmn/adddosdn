import paramiko
import sys
import os

class SSHMiddleware:
    """
    A middleware class to handle SSH connections and operations using Paramiko.
    """
    def __init__(self, hostname, port, username, password):
        """
        Initializes the SSHMiddleware with connection details.

        Args:
            hostname (str): The hostname or IP address of the SSH server.
            port (int): The port number of the SSH server.
            username (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _connect(self):
        """
        Establishes an SSH connection.
        """
        try:
            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            print(f"Successfully connected to {self.hostname}:{self.port}")
            return True
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials.")
        except paramiko.SSHException as sshException:
            print(f"Unable to establish SSH connection: {sshException}")
        except Exception as e:
            print(f"Error connecting to SSH server: {e}")
        return False

    def execute_command(self, command, directory=None):
        """
        Executes a command on the remote server.

        Args:
            command (str): The command to execute.
            directory (str, optional): The directory to execute the command in. Defaults to None.
        """
        if not self._connect():
            return

        remote_command = command
        if directory:
            remote_command = f"cd {directory} && {command}"

        print(f"Executing command: {remote_command}")
        try:
            stdin, stdout, stderr = self.client.exec_command(remote_command)
            print("--- Output ---")
            print(stdout.read().decode())
            err = stderr.read().decode()
            if err:
                print("--- Errors ---")
                print(err)
        except Exception as e:
            print(f"Error executing command: {e}")
        finally:
            self.client.close()

    def copy_file(self, local_path, remote_path):
        """
        Copies a file from the local machine to the remote server.

        Args:
            local_path (str): The path to the local file.
            remote_path (str): The path to the destination on the remote server.
        """
        if not self._connect():
            return

        print(f"Copying {local_path} to {remote_path}...")
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print("File copied successfully.")
        except FileNotFoundError:
            print(f"Error: Local file not found at {local_path}")
        except Exception as e:
            print(f"Error copying file: {e}")
        finally:
            self.client.close()

if __name__ == "__main__":
    # Server details
    HOSTNAME = "jtmksrv"
    PORT = 656
    USERNAME = "user"
    PASSWORD = "1"

    ssh = SSHMiddleware(HOSTNAME, PORT, USERNAME, PASSWORD)

    if len(sys.argv) > 1:
        operation = sys.argv[1]

        if operation == "exec" and len(sys.argv) > 2:
            args = sys.argv[2:]
            command_to_run = ""
            directory_to_run_in = None

            if "--dir" in args:
                try:
                    dir_index = args.index("--dir")
                    directory_to_run_in = args[dir_index + 1]
                    # Remove --dir and its argument from the list
                    command_parts = args[:dir_index] + args[dir_index + 2:]
                    command_to_run = " ".join(command_parts).strip('"')
                except IndexError:
                    print("Error: --dir flag requires a directory path.")
            else:
                command_to_run = " ".join(args).strip('"')
            ssh.execute_command(command_to_run, directory_to_run_in)

        elif operation == "copy" and len(sys.argv) > 3:
            local_file = sys.argv[2]
            remote_file = sys.argv[3]
            ssh.copy_file(local_file, remote_file)

        else:
            print("Usage:")
            print("  python ssh_connect.py exec <command> [--dir <directory>]")
            print("  python ssh_connect.py copy <local_path> <remote_path>")
    else:
        print("Usage:")
        print("  python ssh_connect.py exec <command> [--dir <directory>]")
        print("  python ssh_connect.py copy <local_path> <remote_path>")
