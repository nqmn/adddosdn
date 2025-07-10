#!/usr/bin/env python3
"""
Basic Web GUI for SDN Management - Maximum Compatibility
Uses Python's built-in HTTP server for maximum compatibility
"""

import os
import sys
import subprocess
import json
import urllib.parse
from datetime import datetime

# Python 2/3 compatibility
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs

class SDNManager:
    def __init__(self):
        self.mininet_process = None
        self.ryu_process = None
        self.logs = []
        self.mininet_pid_file = "mininet.pid"
        self.ryu_pid_file = "ryu.pid"

        # Try to restore running processes on startup
        self._restore_processes()

    def log_message(self, message, level="info"):
        """Add a log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.logs.append(log_entry)
        if len(self.logs) > 20:
            self.logs.pop(0)
        print("[{}] {}: {}".format(timestamp, level.upper(), message))

    def _save_pid(self, pid, pid_file):
        """Save process ID to file"""
        try:
            with open(pid_file, 'w') as f:
                f.write(str(pid))
        except:
            pass

    def _load_pid(self, pid_file):
        """Load process ID from file"""
        try:
            with open(pid_file, 'r') as f:
                return int(f.read().strip())
        except:
            return None

    def _remove_pid_file(self, pid_file):
        """Remove PID file"""
        try:
            os.remove(pid_file)
        except:
            pass

    def _is_pid_running(self, pid):
        """Check if a PID is still running"""
        if pid is None:
            return False
        try:
            # On Unix systems, sending signal 0 checks if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
        except AttributeError:
            # Windows doesn't have os.kill, use alternative method
            try:
                import psutil
                return psutil.pid_exists(pid)
            except ImportError:
                # Fallback: try to find process by name
                try:
                    import subprocess
                    result = subprocess.run(['tasklist', '/FI', 'PID eq {}'.format(pid)],
                                          capture_output=True, text=True)
                    return str(pid) in result.stdout
                except:
                    return False

    def _restore_processes(self):
        """Try to restore running processes from PID files"""
        # Check Ryu controller
        ryu_pid = self._load_pid(self.ryu_pid_file)
        if ryu_pid and self._is_pid_running(ryu_pid):
            self.log_message("Found running Ryu controller (PID: {})".format(ryu_pid))
            # Create a dummy process object to track it
            try:
                import psutil
                self.ryu_process = psutil.Process(ryu_pid)
            except:
                # Fallback: we know it's running but can't control it directly
                pass
        else:
            self._remove_pid_file(self.ryu_pid_file)

        # Check Mininet network
        mininet_pid = self._load_pid(self.mininet_pid_file)
        if mininet_pid and self._is_pid_running(mininet_pid):
            self.log_message("Found running Mininet network (PID: {})".format(mininet_pid))
            try:
                import psutil
                self.mininet_process = psutil.Process(mininet_pid)
            except:
                pass
        else:
            self._remove_pid_file(self.mininet_pid_file)

    def is_process_running(self, process):
        """Check if a process is running"""
        if process is None:
            return False

        try:
            # If it's a subprocess.Popen object
            if hasattr(process, 'poll'):
                return process.poll() is None
            # If it's a psutil.Process object
            elif hasattr(process, 'is_running'):
                return process.is_running()
            else:
                return False
        except:
            return False

    def start_ryu_controller(self):
        """Start the Ryu controller"""
        try:
            if self.is_process_running(self.ryu_process):
                self.log_message("Ryu controller is already running", "warning")
                return False

            cmd = [sys.executable, "simple_switch_13.py"]
            self.ryu_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Save PID for persistence
            self._save_pid(self.ryu_process.pid, self.ryu_pid_file)

            self.log_message("Ryu controller started successfully (PID: {})".format(self.ryu_process.pid))
            return True

        except Exception as e:
            self.log_message("Failed to start Ryu controller: {}".format(str(e)), "error")
            return False

    def stop_ryu_controller(self):
        """Stop the Ryu controller"""
        try:
            if self.is_process_running(self.ryu_process):
                if hasattr(self.ryu_process, 'terminate'):
                    # subprocess.Popen object
                    self.ryu_process.terminate()
                    try:
                        self.ryu_process.wait(timeout=10)
                    except:
                        self.ryu_process.kill()
                elif hasattr(self.ryu_process, 'kill'):
                    # psutil.Process object
                    self.ryu_process.kill()

                # Remove PID file
                self._remove_pid_file(self.ryu_pid_file)
                self.ryu_process = None

                self.log_message("Ryu controller stopped")
                return True
            else:
                self.log_message("Ryu controller is not running", "warning")
                return False
        except Exception as e:
            self.log_message("Failed to stop Ryu controller: {}".format(str(e)), "error")
            # Try to remove PID file anyway
            self._remove_pid_file(self.ryu_pid_file)
            return False

    def start_mininet_network(self, interface="ens32"):
        """Start the Mininet network"""
        try:
            if self.is_process_running(self.mininet_process):
                self.log_message("Mininet network is already running", "warning")
                return False

            cmd = [sys.executable, "custom5.py", interface]
            self.mininet_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Save PID for persistence
            self._save_pid(self.mininet_process.pid, self.mininet_pid_file)

            self.log_message("Mininet network started with interface {} (PID: {})".format(interface, self.mininet_process.pid))
            return True

        except Exception as e:
            self.log_message("Failed to start Mininet network: {}".format(str(e)), "error")
            return False

    def stop_mininet_network(self):
        """Stop the Mininet network"""
        try:
            if self.is_process_running(self.mininet_process):
                if hasattr(self.mininet_process, 'stdin'):
                    # subprocess.Popen object - try graceful exit first
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
                elif hasattr(self.mininet_process, 'kill'):
                    # psutil.Process object
                    self.mininet_process.kill()

                # Remove PID file
                self._remove_pid_file(self.mininet_pid_file)
                self.mininet_process = None

                self.log_message("Mininet network stopped")
                return True
            else:
                self.log_message("Mininet network is not running", "warning")
                return False
        except Exception as e:
            self.log_message("Failed to stop Mininet network: {}".format(str(e)), "error")
            # Try to remove PID file anyway
            self._remove_pid_file(self.mininet_pid_file)
            return False

    def execute_mininet_command(self, command):
        """Execute a command in the Mininet CLI"""
        try:
            if not self.is_process_running(self.mininet_process):
                return False

            command_bytes = (command + "\n").encode()
            self.mininet_process.stdin.write(command_bytes)
            self.mininet_process.stdin.flush()

            self.log_message("Executed command: {}".format(command))
            return True

        except Exception as e:
            self.log_message("Command failed: {}".format(str(e)), "error")
            return False

    def get_status(self):
        """Get system status"""
        # Check if processes are still running, and if not, try to restore from PIDs
        controller_running = self.is_process_running(self.ryu_process)
        if not controller_running:
            # Try to restore from PID file
            ryu_pid = self._load_pid(self.ryu_pid_file)
            if ryu_pid and self._is_pid_running(ryu_pid):
                try:
                    import psutil
                    self.ryu_process = psutil.Process(ryu_pid)
                    controller_running = True
                except:
                    self._remove_pid_file(self.ryu_pid_file)

        network_running = self.is_process_running(self.mininet_process)
        if not network_running:
            # Try to restore from PID file
            mininet_pid = self._load_pid(self.mininet_pid_file)
            if mininet_pid and self._is_pid_running(mininet_pid):
                try:
                    import psutil
                    self.mininet_process = psutil.Process(mininet_pid)
                    network_running = True
                except:
                    self._remove_pid_file(self.mininet_pid_file)

        return {
            'controller_status': 'running' if controller_running else 'stopped',
            'network_status': 'running' if network_running else 'stopped'
        }

# Global SDN manager instance
sdn_manager = SDNManager()

class SDNRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to reduce server logging"""
        pass

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == '/':
            self.serve_main_page()
        elif path == '/start_controller':
            sdn_manager.start_ryu_controller()
            self.redirect_home()
        elif path == '/stop_controller':
            sdn_manager.stop_ryu_controller()
            self.redirect_home()
        elif path == '/start_network':
            interface = query.get('interface', ['ens32'])[0]
            sdn_manager.start_mininet_network(interface)
            self.redirect_home()
        elif path == '/stop_network':
            sdn_manager.stop_mininet_network()
            self.redirect_home()
        elif path == '/api/status':
            self.serve_json(sdn_manager.get_status())
        elif path == '/api/logs':
            self.serve_json({'logs': sdn_manager.logs})
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/execute_command':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')

            # Parse form data
            params = parse_qs(post_data)
            command = params.get('command', [''])[0]

            if command:
                sdn_manager.execute_mininet_command(command)

            self.redirect_home()
        else:
            self.send_error(404)

    def serve_main_page(self):
        """Serve the main HTML page"""
        status = sdn_manager.get_status()
        logs = sdn_manager.logs[-10:]  # Last 10 logs

        html = self.generate_html(status, logs)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_json(self, data):
        """Serve JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def redirect_home(self):
        """Redirect to home page"""
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def generate_html(self, status, logs):
        """Generate the HTML page"""
        controller_status_class = "running" if status['controller_status'] == 'running' else "stopped"
        network_status_class = "running" if status['network_status'] == 'running' else "stopped"

        logs_html = ""
        for log in logs:
            logs_html += '<div class="log-entry log-{}">[{}] {}</div>\n'.format(
                log['level'], log['timestamp'], log['message']
            )

        if not logs_html:
            logs_html = '<div class="log-entry log-info">[System] Web GUI ready. Start controller first, then network.</div>'

        html = '''<!DOCTYPE html>
<html>
<head>
    <title>Basic SDN Web GUI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; }}
        .main {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px; }}
        .panel {{ border: 2px solid #ecf0f1; border-radius: 8px; overflow: hidden; }}
        .panel-header {{ background: #34495e; color: white; padding: 15px; font-weight: bold; }}
        .panel-content {{ padding: 20px; }}
        .status {{ font-size: 1.2em; margin-bottom: 20px; padding: 10px; border-radius: 5px; text-align: center; }}
        .status.running {{ background: #d4edda; color: #155724; }}
        .status.stopped {{ background: #f8d7da; color: #721c24; }}
        .btn {{ background: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }}
        .btn:hover {{ background: #2980b9; }}
        .btn-danger {{ background: #e74c3c; }}
        .btn-success {{ background: #27ae60; }}
        .input-group {{ margin: 15px 0; }}
        .input-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        .input-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        .command-form {{ display: flex; gap: 10px; margin: 15px 0; }}
        .command-form input {{ flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .logs {{ grid-column: 1 / -1; margin-top: 20px; }}
        .logs-container {{ background: #2c3e50; color: white; padding: 15px; border-radius: 5px; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.9em; }}
        .log-entry {{ margin-bottom: 5px; }}
        .log-info {{ color: #3498db; }}
        .log-warning {{ color: #f39c12; }}
        .log-error {{ color: #e74c3c; }}
        .topology {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px; font-family: monospace; font-size: 0.9em; text-align: center; }}
        .refresh-btn {{ position: fixed; top: 20px; right: 20px; background: #27ae60; color: white; border: none; padding: 10px 15px; border-radius: 20px; cursor: pointer; }}
        @media (max-width: 768px) {{ .main {{ grid-template-columns: 1fr; }} }}
    </style>
    <script>setTimeout(function(){{window.location.reload();}}, 30000);</script>
</head>
<body>
    <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh</button>
    <div class="container">
        <div class="header">
            <h1>🌐 Basic SDN Web GUI</h1>
            <p>Mininet Network & Ryu Controller Management</p>
        </div>
        <div class="main">
            <div class="panel">
                <div class="panel-header">🎛️ Ryu Controller</div>
                <div class="panel-content">
                    <div class="status {}">{}</div>
                    <div style="text-align: center;">
                        {}
                    </div>
                    <div class="topology">
                        <strong>Controller Info:</strong><br>
                        📡 Ryu Controller<br>
                        ├── OpenFlow 1.3<br>
                        ├── MAC Learning<br>
                        └── Flow Management
                    </div>
                </div>
            </div>
            <div class="panel">
                <div class="panel-header">🌐 Mininet Network</div>
                <div class="panel-content">
                    <div class="status {}">{}</div>
                    {}
                    <div class="topology">
                        <strong>Network Topology:</strong><br>
                        🖥️ Hardware Interface<br>
                        │<br>
                        🔄 Switch (s1)<br>
                        ├── 💻 h2 (10.0.0.2)<br>
                        ├── 💻 h3 (10.0.0.3)<br>
                        ├── 💻 h4 (10.0.0.4)<br>
                        └── 💻 h5 (10.0.0.5)
                    </div>
                </div>
            </div>
        </div>
        <div class="panel logs">
            <div class="panel-header">📋 Recent Logs</div>
            <div class="panel-content">
                <div class="logs-container">
                    {}
                </div>
                <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                    Page auto-refreshes every 30 seconds. Click refresh for immediate update.
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''.format(
            controller_status_class,
            status['controller_status'].title(),
            '<a href="/start_controller" class="btn btn-success">▶️ Start Controller</a>' if status['controller_status'] == 'stopped' else '<a href="/stop_controller" class="btn btn-danger">⏹️ Stop Controller</a>',
            network_status_class,
            status['network_status'].title(),
            '''<form action="/start_network" method="get">
                <div class="input-group">
                    <label>Hardware Interface:</label>
                    <input type="text" name="interface" value="ens32" placeholder="Enter interface name">
                </div>
                <div style="text-align: center;">
                    <button type="submit" class="btn btn-success">▶️ Start Network</button>
                </div>
            </form>''' if status['network_status'] == 'stopped' else '''<div style="text-align: center;">
                <a href="/stop_network" class="btn btn-danger">⏹️ Stop Network</a>
            </div>
            <form action="/execute_command" method="post">
                <div class="command-form">
                    <input type="text" name="command" placeholder="Enter command (e.g., pingall, h2 ping h3)">
                    <button type="submit" class="btn">Execute</button>
                </div>
            </form>''',
            logs_html
        )

        return html

def main():
    print("🌐 Starting Basic SDN Web GUI...")
    print("📍 Access the interface at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)

    # Initialize with a welcome message
    sdn_manager.log_message("Basic Web GUI initialized. Ready to manage SDN components.")

    try:
        server = HTTPServer(('0.0.0.0', 5000), SDNRequestHandler)
        print("✅ Server started successfully!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        # Clean up processes
        sdn_manager.stop_ryu_controller()
        sdn_manager.stop_mininet_network()
    except Exception as e:
        print("❌ Error starting server: {}".format(e))

if __name__ == '__main__':
    main()
