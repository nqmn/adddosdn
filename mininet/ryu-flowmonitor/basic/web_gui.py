#!/usr/bin/env python3
"""
Web-based GUI for Mininet and Ryu Controller Management
Provides a web interface to control and monitor the basic SDN setup
"""

import os
import sys
import json
import threading
import subprocess
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import psutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdn_gui_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class SDNManager:
    def __init__(self):
        self.mininet_process = None
        self.ryu_process = None
        self.network_status = "stopped"
        self.controller_status = "stopped"
        self.flow_stats = {}
        self.mac_table = {}
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
        if len(self.logs) > 100:  # Keep only last 100 logs
            self.logs.pop(0)

        # Emit to all connected clients
        socketio.emit('log_update', log_entry)

    def start_ryu_controller(self):
        """Start the Ryu controller"""
        try:
            if self.ryu_process and self.ryu_process.poll() is None:
                self.log_message("Ryu controller is already running", "warning")
                return False

            # Start Ryu controller
            cmd = [sys.executable, "simple_switch_13.py"]
            self.ryu_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.controller_status = "running"
            self.log_message("Ryu controller started successfully")

            # Start monitoring thread
            threading.Thread(target=self._monitor_ryu, daemon=True).start()
            return True

        except Exception as e:
            self.log_message(f"Failed to start Ryu controller: {str(e)}", "error")
            return False

    def stop_ryu_controller(self):
        """Stop the Ryu controller"""
        try:
            if self.ryu_process and self.ryu_process.poll() is None:
                self.ryu_process.terminate()
                self.ryu_process.wait(timeout=10)
                self.controller_status = "stopped"
                self.log_message("Ryu controller stopped")
                return True
            else:
                self.log_message("Ryu controller is not running", "warning")
                return False
        except Exception as e:
            self.log_message(f"Failed to stop Ryu controller: {str(e)}", "error")
            return False

    def start_mininet_network(self, interface="ens32"):
        """Start the Mininet network"""
        try:
            if self.mininet_process and self.mininet_process.poll() is None:
                self.log_message("Mininet network is already running", "warning")
                return False

            # Start Mininet network
            cmd = [sys.executable, "custom5.py", interface]
            self.mininet_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.network_status = "running"
            self.log_message(f"Mininet network started with interface {interface}")

            # Start monitoring thread
            threading.Thread(target=self._monitor_mininet, daemon=True).start()
            return True

        except Exception as e:
            self.log_message(f"Failed to start Mininet network: {str(e)}", "error")
            return False

    def stop_mininet_network(self):
        """Stop the Mininet network"""
        try:
            if self.mininet_process and self.mininet_process.poll() is None:
                # Send exit command to Mininet CLI
                self.mininet_process.stdin.write("exit\n")
                self.mininet_process.stdin.flush()
                self.mininet_process.wait(timeout=10)
                self.network_status = "stopped"
                self.log_message("Mininet network stopped")
                return True
            else:
                self.log_message("Mininet network is not running", "warning")
                return False
        except Exception as e:
            self.log_message(f"Failed to stop Mininet network: {str(e)}", "error")
            return False

    def execute_mininet_command(self, command):
        """Execute a command in the Mininet CLI"""
        try:
            if not self.mininet_process or self.mininet_process.poll() is not None:
                return {"success": False, "output": "Mininet network is not running"}

            self.mininet_process.stdin.write(f"{command}\n")
            self.mininet_process.stdin.flush()

            # Note: In a real implementation, you'd need to capture the output
            # This is simplified for the basic version
            self.log_message(f"Executed command: {command}")
            return {"success": True, "output": f"Command '{command}' executed"}

        except Exception as e:
            return {"success": False, "output": f"Error: {str(e)}"}

    def _monitor_ryu(self):
        """Monitor Ryu controller process"""
        while self.ryu_process and self.ryu_process.poll() is None:
            time.sleep(5)
            # Emit status update
            socketio.emit('controller_status', {
                'status': self.controller_status,
                'pid': self.ryu_process.pid if self.ryu_process else None
            })

        if self.controller_status == "running":
            self.controller_status = "stopped"
            self.log_message("Ryu controller process ended", "warning")

    def _monitor_mininet(self):
        """Monitor Mininet network process"""
        while self.mininet_process and self.mininet_process.poll() is None:
            time.sleep(5)
            # Emit status update
            socketio.emit('network_status', {
                'status': self.network_status,
                'pid': self.mininet_process.pid if self.mininet_process else None
            })

        if self.network_status == "running":
            self.network_status = "stopped"
            self.log_message("Mininet network process ended", "warning")

    def get_system_info(self):
        """Get system information"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'network_status': self.network_status,
            'controller_status': self.controller_status
        }

# Global SDN manager instance
sdn_manager = SDNManager()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/start_controller', methods=['POST'])
def start_controller():
    """Start Ryu controller"""
    success = sdn_manager.start_ryu_controller()
    return jsonify({'success': success})

@app.route('/api/stop_controller', methods=['POST'])
def stop_controller():
    """Stop Ryu controller"""
    success = sdn_manager.stop_ryu_controller()
    return jsonify({'success': success})

@app.route('/api/start_network', methods=['POST'])
def start_network():
    """Start Mininet network"""
    interface = request.json.get('interface', 'ens32')
    success = sdn_manager.start_mininet_network(interface)
    return jsonify({'success': success})

@app.route('/api/stop_network', methods=['POST'])
def stop_network():
    """Stop Mininet network"""
    success = sdn_manager.stop_mininet_network()
    return jsonify({'success': success})

@app.route('/api/execute_command', methods=['POST'])
def execute_command():
    """Execute Mininet command"""
    command = request.json.get('command', '')
    result = sdn_manager.execute_mininet_command(command)
    return jsonify(result)

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify(sdn_manager.get_system_info())

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    return jsonify({'logs': sdn_manager.logs})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status_update', sdn_manager.get_system_info())
    emit('logs_update', {'logs': sdn_manager.logs})

@socketio.on('request_status')
def handle_status_request():
    """Handle status request"""
    emit('status_update', sdn_manager.get_system_info())

if __name__ == '__main__':
    # Start the web server
    print("Starting SDN Web GUI...")
    print("Access the interface at: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
