#!/usr/bin/env python3
"""
Minimal Web GUI for Mininet and Ryu Controller Management
Compatible with Flask 1.1.4 and older Python versions
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdn_gui_secret_key'

class MinimalSDNManager:
    def __init__(self):
        self.mininet_process = None
        self.ryu_process = None
        self.logs = []

    def log_message(self, message, level="info"):
        """Add a log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.logs.append(log_entry)
        if len(self.logs) > 50:  # Keep only last 50 logs
            self.logs.pop(0)
        print(f"[{timestamp}] {level.upper()}: {message}")

    def is_process_running(self, process):
        """Check if a process is running"""
        return process is not None and process.poll() is None

    def start_ryu_controller(self):
        """Start the Ryu controller"""
        try:
            if self.is_process_running(self.ryu_process):
                self.log_message("Ryu controller is already running", "warning")
                return False

            # Start Ryu controller
            cmd = [sys.executable, "simple_switch_13.py"]
            self.ryu_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.log_message("Ryu controller started successfully")
            return True

        except Exception as e:
            self.log_message("Failed to start Ryu controller: {}".format(str(e)), "error")
            return False

    def stop_ryu_controller(self):
        """Stop the Ryu controller"""
        try:
            if self.is_process_running(self.ryu_process):
                self.ryu_process.terminate()
                try:
                    self.ryu_process.wait(timeout=10)
                except:
                    self.ryu_process.kill()
                self.log_message("Ryu controller stopped")
                return True
            else:
                self.log_message("Ryu controller is not running", "warning")
                return False
        except Exception as e:
            self.log_message("Failed to stop Ryu controller: {}".format(str(e)), "error")
            return False

    def start_mininet_network(self, interface="ens32"):
        """Start the Mininet network"""
        try:
            if self.is_process_running(self.mininet_process):
                self.log_message("Mininet network is already running", "warning")
                return False

            # Start Mininet network
            cmd = [sys.executable, "custom5.py", interface]
            self.mininet_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.log_message("Mininet network started with interface {}".format(interface))
            return True

        except Exception as e:
            self.log_message("Failed to start Mininet network: {}".format(str(e)), "error")
            return False

    def stop_mininet_network(self):
        """Stop the Mininet network"""
        try:
            if self.is_process_running(self.mininet_process):
                # Send exit command to Mininet CLI
                try:
                    self.mininet_process.stdin.write(b"exit\n")
                    self.mininet_process.stdin.flush()
                    self.mininet_process.wait(timeout=10)
                except:
                    self.mininet_process.terminate()
                    try:
                        self.mininet_process.wait(timeout=5)
                    except:
                        self.mininet_process.kill()

                self.log_message("Mininet network stopped")
                return True
            else:
                self.log_message("Mininet network is not running", "warning")
                return False
        except Exception as e:
            self.log_message("Failed to stop Mininet network: {}".format(str(e)), "error")
            return False

    def execute_mininet_command(self, command):
        """Execute a command in the Mininet CLI"""
        try:
            if not self.is_process_running(self.mininet_process):
                return {"success": False, "output": "Mininet network is not running"}

            command_bytes = (command + "\n").encode()
            self.mininet_process.stdin.write(command_bytes)
            self.mininet_process.stdin.flush()

            self.log_message("Executed command: {}".format(command))
            return {"success": True, "output": "Command '{}' executed".format(command)}

        except Exception as e:
            return {"success": False, "output": "Error: {}".format(str(e))}

    def get_status(self):
        """Get system status"""
        controller_running = self.is_process_running(self.ryu_process)
        network_running = self.is_process_running(self.mininet_process)

        return {
            'controller_status': 'running' if controller_running else 'stopped',
            'network_status': 'running' if network_running else 'stopped'
        }

# Global SDN manager instance
sdn_manager = MinimalSDNManager()

@app.route('/')
def index():
    """Main page"""
    status = sdn_manager.get_status()
    return render_template('minimal_index.html', status=status, logs=sdn_manager.logs[-10:])

@app.route('/start_controller')
def start_controller():
    """Start Ryu controller"""
    sdn_manager.start_ryu_controller()
    return redirect(url_for('index'))

@app.route('/stop_controller')
def stop_controller():
    """Stop Ryu controller"""
    sdn_manager.stop_ryu_controller()
    return redirect(url_for('index'))

@app.route('/start_network')
def start_network():
    """Start Mininet network"""
    interface = request.args.get('interface', 'ens32')
    sdn_manager.start_mininet_network(interface)
    return redirect(url_for('index'))

@app.route('/stop_network')
def stop_network():
    """Stop Mininet network"""
    sdn_manager.stop_mininet_network()
    return redirect(url_for('index'))

@app.route('/execute_command', methods=['POST'])
def execute_command():
    """Execute Mininet command"""
    command = request.form.get('command', '')
    if command:
        result = sdn_manager.execute_mininet_command(command)
        sdn_manager.log_message("Command result: {}".format(result['output']))
    return redirect(url_for('index'))

@app.route('/api/status')
def get_status():
    """Get system status as JSON"""
    return jsonify(sdn_manager.get_status())

@app.route('/api/logs')
def get_logs():
    """Get recent logs as JSON"""
    return jsonify({'logs': sdn_manager.logs})

if __name__ == '__main__':
    print("🌐 Starting Minimal SDN Web GUI...")
    print("📍 Access the interface at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")

    # Initialize with a welcome message
    sdn_manager.log_message("Web GUI initialized. Ready to manage SDN components.")

    try:
        # Use threaded mode for better compatibility
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        # Clean up processes
        sdn_manager.stop_ryu_controller()
        sdn_manager.stop_mininet_network()
    except Exception as e:
        print("❌ Error starting server: {}".format(e))
        print("💡 Trying alternative startup method...")
        try:
            # Alternative method for older Flask versions
            from werkzeug.serving import run_simple
            run_simple('0.0.0.0', 5000, app, threaded=True, use_reloader=False)
        except Exception as e2:
            print("❌ Alternative method also failed: {}".format(e2))
