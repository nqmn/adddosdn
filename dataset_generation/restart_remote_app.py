import subprocess
import os

# Define the path to your ssh_connect.py script
SSH_CONNECT_SCRIPT = "C:/Users/Intel/Desktop/InSDN_ddos_dataset/adversarial-ddos-attacks-sdn-dataset/dataset_generation/ssh_connect.py"

# Define the remote directory where your project is located
REMOTE_PROJECT_DIR = "/home/user/dataset_generation"

def run_remote_command(command, description):
    """Helper function to run a command on the remote server using ssh_connect.py"""
    full_command = [
        "python",
        SSH_CONNECT_SCRIPT,
        "exec",
        command,
        "--dir",
        REMOTE_PROJECT_DIR
    ]
    print(f"Executing: {description}")
    try:
        result = subprocess.run(full_command, capture_output=True, text=True, check=True)
        print("STDOUT:\n", result.stdout)
        if result.stderr:
            print("STDERR:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
    except FileNotFoundError:
        print(f"Error: {SSH_CONNECT_SCRIPT} not found. Please check the path.")

if __name__ == "__main__":
    print("Stopping main.py and ryu-manager, cleaning Mininet, and restarting main.py on the remote server...")

    # Combine all commands into a single string to be executed sequentially
    combined_command = (
        "sudo pkill -9 -f main.py && "
        "sudo pkill -9 -f ryu-manager && "
        "sudo mn -c && "
        f"sudo nohup python3 main.py > output.log 2>&1 &"
    )

    run_remote_command(combined_command, "Stopping processes, cleaning Mininet, and restarting main.py")

    print("\nProcess automation complete. Check output.log on the remote server for details.")
    print("You can check the status with: python ssh_connect.py exec \"pgrep -f main.py\"")
    print("And view logs with: python ssh_connect.py exec \"cat /home/user/dataset_generation/output.log\"")
