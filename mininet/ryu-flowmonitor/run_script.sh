#!/bin/bash

# Ryu Flow Monitor - Quick Start Script
# This script helps you quickly set up and run the Ryu Flow Monitor

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RYU_CONTROLLER_FILE="flow_monitor_controller.py"
WEB_INTERFACE_FILE="flow_monitor.html"
CONTROLLER_PORT=8080
OPENFLOW_PORT=6633

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "     Ryu Flow Monitor - Quick Start Script"
    echo "=================================================="
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Ryu
    if ! python3 -c "import ryu" 2>/dev/null; then
        print_error "Ryu framework is not installed"
        echo "Install with: pip install ryu"
        exit 1
    fi
    
    # Check if controller file exists
    if [ ! -f "$RYU_CONTROLLER_FILE" ]; then
        print_error "Controller file '$RYU_CONTROLLER_FILE' not found"
        echo "Please save the Python controller code as '$RYU_CONTROLLER_FILE'"
        exit 1
    fi
    
    # Check if web interface exists
    if [ ! -f "$WEB_INTERFACE_FILE" ]; then
        print_error "Web interface file '$WEB_INTERFACE_FILE' not found"
        echo "Please save the HTML code as '$WEB_INTERFACE_FILE'"
        exit 1
    fi
    
    print_status "All dependencies found!"
}

check_ports() {
    print_status "Checking if ports are available..."
    
    # Check if controller port is in use
    if lsof -Pi :$CONTROLLER_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $CONTROLLER_PORT is already in use"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check if OpenFlow port is in use
    if lsof -Pi :$OPENFLOW_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "OpenFlow port $OPENFLOW_PORT is already in use"
        print_warning "Another controller might be running"
    fi
}

start_controller() {
    print_status "Starting Ryu controller..."
    echo "Controller will run on port $CONTROLLER_PORT"
    echo "OpenFlow port: $OPENFLOW_PORT"
    echo "Press Ctrl+C to stop the controller"
    echo ""
    
    # Start Ryu controller with topology discovery
    ryu-manager "$RYU_CONTROLLER_FILE" --observe-links \
        --wsapi-port "$CONTROLLER_PORT" \
        --ofp-tcp-listen-port "$OPENFLOW_PORT" \
        --verbose
}

start_mininet_demo() {
    print_status "Starting Mininet demo topology..."
    
    # Check if Mininet is installed
    if ! command -v mn &> /dev/null; then
        print_error "Mininet is not installed"
        echo "Install with: sudo apt-get install mininet"
        return 1
    fi
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "Mininet requires root privileges"
        echo "Run with sudo or start Mininet manually"
        return 1
    fi
    
    print_status "Creating linear topology with 3 switches..."
    mn --topo linear,3 \
       --controller remote,ip=127.0.0.1,port=$OPENFLOW_PORT \
       --switch ovsk,protocols=OpenFlow13
}

open_web_interface() {
    print_status "Opening web interface..."
    
    # Try to open web browser
    if command -v xdg-open > /dev/null; then
        xdg-open "$WEB_INTERFACE_FILE"
    elif command -v open > /dev/null; then
        open "$WEB_INTERFACE_FILE"
    elif command -v start > /dev/null; then
        start "$WEB_INTERFACE_FILE"
    else
        print_warning "Could not open web browser automatically"
        echo "Please open '$WEB_INTERFACE_FILE' in your web browser"
    fi
}

show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start           Start the Ryu controller"
    echo "  demo            Start controller and Mininet demo"
    echo "  web             Open web interface"
    echo "  check           Check dependencies only"
    echo "  help            Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start        # Start controller only"
    echo "  $0 demo         # Start controller + Mininet demo"
    echo "  $0 web          # Open web interface"
}

show_instructions() {
    echo ""
    print_status "Quick Start Instructions:"
    echo ""
    echo "1. Start the controller:"
    echo "   $0 start"
    echo ""
    echo "2. In another terminal, start Mininet (requires sudo):"
    echo "   sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=$OPENFLOW_PORT --switch ovsk,protocols=OpenFlow13"
    echo ""
    echo "3. Open the web interface:"
    echo "   $0 web"
    echo ""
    echo "4. In Mininet, generate some traffic:"
    echo "   mininet> h1 ping h3"
    echo "   mininet> iperf h1 h2"
    echo ""
    echo "5. Watch the flow monitor update in real-time!"
    echo ""
}

cleanup() {
    print_status "Cleaning up..."
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
}

# Set up signal handling
trap cleanup EXIT

# Main script logic
print_header

case "${1:-start}" in
    "start")
        check_dependencies
        check_ports
        start_controller
        ;;
    "demo")
        check_dependencies
        check_ports
        echo "Starting demo mode..."
        echo "This will start both the controller and Mininet"
        echo ""
        
        # Start controller in background
        print_status "Starting controller in background..."
        ryu-manager "$RYU_CONTROLLER_FILE" --observe-links \
            --wsapi-port "$CONTROLLER_PORT" \
            --ofp-tcp-listen-port "$OPENFLOW_PORT" &
        
        # Wait a moment for controller to start
        sleep 3
        
        # Start Mininet
        start_mininet_demo
        ;;
    "web")
        open_web_interface
        ;;
    "check")
        check_dependencies
        print_status "All checks passed!"
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac

if [ "$1" = "start" ]; then
    show_instructions
fi