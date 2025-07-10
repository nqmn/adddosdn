#!/usr/bin/env python3
"""
Simple Web GUI for Mininet and Ryu Controller Management (No WebSocket)
A fallback version that works without real-time updates
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
import psutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdn_gui_secret_key'

class SimpleSDNManager:
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
        if len(self.logs) > 100:  # Keep only last 100 logs
            self.logs.pop(0)
    
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
            
            self.log_message("Ryu controller started successfully")
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
            
            self.log_message(f"Mininet network started with interface {interface}")
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
            
            self.log_message(f"Executed command: {command}")
            return {"success": True, "output": f"Command '{command}' executed"}
            
        except Exception as e:
            return {"success": False, "output": f"Error: {str(e)}"}
    
    def get_status(self):
        """Get system status"""
        controller_running = self.ryu_process and self.ryu_process.poll() is None
        network_running = self.mininet_process and self.mininet_process.poll() is None
        
        return {
            'controller_status': 'running' if controller_running else 'stopped',
            'network_status': 'running' if network_running else 'stopped',
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent
        }

# Global SDN manager instance
sdn_manager = SimpleSDNManager()

@app.route('/')
def index():
    """Main page"""
    status = sdn_manager.get_status()
    return render_template('simple_index.html', status=status, logs=sdn_manager.logs)

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
        sdn_manager.log_message(f"Command result: {result['output']}")
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
    print("🌐 Starting Simple SDN Web GUI...")
    print("📍 Access the interface at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5000, debug=True)
