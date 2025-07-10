#!/bin/bash

# Enhanced Ryu Flow Monitor Run Script with DDoS Detection
# This script provides easy commands to start, stop, and manage the Enhanced Ryu Flow Monitor system
# Supports both root controller and client controller modes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ROOT_CONTROLLER_FILE="flow_monitor_controller.py"
CLIENT_CONTROLLER_FILE="mininet_client_controller.py"
WEB_INTERFACE_FILE="flow_monitor.html"

# Default ports
ROOT_CONTROLLER_PORT=8080
CLIENT_CONTROLLER_PORT=8081
ROOT_OPENFLOW_PORT=6633
CLIENT_OPENFLOW_PORT=6634
FEDERATED_PORT=9999

# Default addresses
ROOT_ADDRESS="192.168.1.100"
CLIENT_ADDRESS="192.168.1.101"

# Process tracking
CONTROLLER_PID_FILE="/tmp/ryu_controller.pid"
MININET_PID_FILE="/tmp/mininet.pid"

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "  Enhanced Ryu Flow Monitor with DDoS Detection"
    echo "  Multi-Controller SDN Security System"
    echo "=================================================================="
    echo -e "${NC}"
}

print_usage() {
    echo -e "${CYAN}Usage: $0 [COMMAND] [OPTIONS]${NC}"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  root-start      Start root controller (Ryu server)"
    echo "  client-start    Start client controller (Mininet server)"
    echo "  mininet-start   Start Mininet network"
    echo "  web             Open web interface"
    echo "  stop            Stop all services"
    echo "  status          Show system status"
    echo "  test-ddos       Run DDoS attack simulation"
    echo "  check-deps      Check dependencies"
    echo "  logs            Show controller logs"
    echo "  monitor         Real-time monitoring"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --root-ip IP    Root controller IP (default: $ROOT_ADDRESS)"
    echo "  --client-ip IP  Client controller IP (default: $CLIENT_ADDRESS)"
    echo "  --verbose       Enable verbose logging"
    echo "  --help          Show this help message"
}

check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Python 3 found${NC}"
    fi
    
    # Check Ryu
    if ! python3 -c "import ryu" 2>/dev/null; then
        echo -e "${RED}❌ Ryu framework not found${NC}"
        echo "Install with: pip install ryu"
        exit 1
    else
        echo -e "${GREEN}✅ Ryu framework found${NC}"
    fi
    
    # Check ML packages
    if ! python3 -c "import sklearn, pandas, numpy" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  ML packages not found (optional)${NC}"
        echo "Install with: pip install scikit-learn pandas numpy"
    else
        echo -e "${GREEN}✅ ML packages found${NC}"
    fi
    
    # Check CICFlowMeter
    if ! command -v cicflowmeter &> /dev/null; then
        echo -e "${YELLOW}⚠️  CICFlowMeter not found (optional)${NC}"
        echo "Install with: pip install cicflowmeter"
    else
        echo -e "${GREEN}✅ CICFlowMeter found${NC}"
    fi
    
    # Check Mininet (only if on Mininet server)
    if command -v mn &> /dev/null; then
        echo -e "${GREEN}✅ Mininet found${NC}"
    else
        echo -e "${YELLOW}⚠️  Mininet not found (only needed on Mininet server)${NC}"
    fi
    
    echo -e "${GREEN}Dependency check completed${NC}"
}

start_root_controller() {
    echo -e "${BLUE}Starting Root Controller...${NC}"
    
    if [ -f "$CONTROLLER_PID_FILE" ] && kill -0 $(cat "$CONTROLLER_PID_FILE") 2>/dev/null; then
        echo -e "${YELLOW}Root controller already running (PID: $(cat $CONTROLLER_PID_FILE))${NC}"
        return
    fi
    
    # Create logs directory
    mkdir -p logs
    
    # Start root controller
    echo -e "${CYAN}Starting root controller on port $ROOT_CONTROLLER_PORT...${NC}"
    
    if [ "$VERBOSE" = true ]; then
        python3 "$ROOT_CONTROLLER_FILE" \
            --controller-id root_controller \
            --is-root true \
            --wsapi-port "$ROOT_CONTROLLER_PORT" \
            --ofp-tcp-listen-port "$ROOT_OPENFLOW_PORT" \
            --verbose &
    else
        python3 "$ROOT_CONTROLLER_FILE" \
            --controller-id root_controller \
            --is-root true \
            --wsapi-port "$ROOT_CONTROLLER_PORT" \
            --ofp-tcp-listen-port "$ROOT_OPENFLOW_PORT" \
            > logs/root_controller.log 2>&1 &
    fi
    
    echo $! > "$CONTROLLER_PID_FILE"
    
    # Wait for controller to start
    sleep 3
    
    if kill -0 $(cat "$CONTROLLER_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}✅ Root controller started successfully${NC}"
        echo -e "${CYAN}   PID: $(cat $CONTROLLER_PID_FILE)${NC}"
        echo -e "${CYAN}   REST API: http://$ROOT_ADDRESS:$ROOT_CONTROLLER_PORT${NC}"
        echo -e "${CYAN}   OpenFlow: $ROOT_ADDRESS:$ROOT_OPENFLOW_PORT${NC}"
        echo -e "${CYAN}   Federated Learning: $ROOT_ADDRESS:$FEDERATED_PORT${NC}"
    else
        echo -e "${RED}❌ Failed to start root controller${NC}"
        rm -f "$CONTROLLER_PID_FILE"
        exit 1
    fi
}

start_client_controller() {
    echo -e "${BLUE}Starting Client Controller...${NC}"
    
    # Create logs directory
    mkdir -p logs
    
    # Start client controller
    echo -e "${CYAN}Starting client controller on port $CLIENT_CONTROLLER_PORT...${NC}"
    
    if [ "$VERBOSE" = true ]; then
        python3 "$CLIENT_CONTROLLER_FILE" \
            --controller-id mininet_client_1 \
            --root-address "$ROOT_ADDRESS:$FEDERATED_PORT" \
            --wsapi-port "$CLIENT_CONTROLLER_PORT" \
            --ofp-tcp-listen-port "$CLIENT_OPENFLOW_PORT" \
            --verbose &
    else
        python3 "$CLIENT_CONTROLLER_FILE" \
            --controller-id mininet_client_1 \
            --root-address "$ROOT_ADDRESS:$FEDERATED_PORT" \
            --wsapi-port "$CLIENT_CONTROLLER_PORT" \
            --ofp-tcp-listen-port "$CLIENT_OPENFLOW_PORT" \
            > logs/client_controller.log 2>&1 &
    fi
    
    CLIENT_PID=$!
    
    # Wait for controller to start
    sleep 3
    
    if kill -0 $CLIENT_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Client controller started successfully${NC}"
        echo -e "${CYAN}   PID: $CLIENT_PID${NC}"
        echo -e "${CYAN}   REST API: http://$CLIENT_ADDRESS:$CLIENT_CONTROLLER_PORT${NC}"
        echo -e "${CYAN}   OpenFlow: $CLIENT_ADDRESS:$CLIENT_OPENFLOW_PORT${NC}"
        echo -e "${CYAN}   Root Connection: $ROOT_ADDRESS:$FEDERATED_PORT${NC}"
    else
        echo -e "${RED}❌ Failed to start client controller${NC}"
        exit 1
    fi
}

start_mininet() {
    echo -e "${BLUE}Starting Mininet Network...${NC}"
    
    if [ -f "$MININET_PID_FILE" ] && kill -0 $(cat "$MININET_PID_FILE") 2>/dev/null; then
        echo -e "${YELLOW}Mininet already running (PID: $(cat $MININET_PID_FILE))${NC}"
        return
    fi
    
    # Clean up any existing Mininet processes
    sudo mn -c > /dev/null 2>&1 || true
    
    echo -e "${CYAN}Creating linear topology with 5 switches...${NC}"
    
    # Start Mininet with linear topology
    sudo mn --topo linear,5 \
        --controller remote,ip=127.0.0.1,port="$CLIENT_OPENFLOW_PORT" \
        --switch ovsk,protocols=OpenFlow13 \
        --link tc,bw=100 \
        --mac &
    
    echo $! > "$MININET_PID_FILE"
    
    sleep 5
    
    echo -e "${GREEN}✅ Mininet network started${NC}"
    echo -e "${CYAN}   Topology: Linear with 5 switches${NC}"
    echo -e "${CYAN}   Controller: 127.0.0.1:$CLIENT_OPENFLOW_PORT${NC}"
    echo -e "${CYAN}   Use 'sudo mn -c' to clean up when done${NC}"
}

open_web_interface() {
    echo -e "${BLUE}Opening Web Interface...${NC}"
    
    # Check if controllers are running
    if ! curl -s "http://$ROOT_ADDRESS:$ROOT_CONTROLLER_PORT/stats" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Root controller not responding${NC}"
    fi
    
    if ! curl -s "http://$CLIENT_ADDRESS:$CLIENT_CONTROLLER_PORT/stats" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Client controller not responding${NC}"
    fi
    
    # Open web interfaces
    echo -e "${CYAN}Opening web interfaces...${NC}"
    echo -e "${CYAN}   Root Controller: http://$ROOT_ADDRESS:$ROOT_CONTROLLER_PORT/$WEB_INTERFACE_FILE${NC}"
    echo -e "${CYAN}   Client Controller: http://$CLIENT_ADDRESS:$CLIENT_CONTROLLER_PORT/$WEB_INTERFACE_FILE${NC}"
    
    # Try to open in browser
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://$ROOT_ADDRESS:$ROOT_CONTROLLER_PORT/$WEB_INTERFACE_FILE" 2>/dev/null &
    elif command -v open &> /dev/null; then
        open "http://$ROOT_ADDRESS:$ROOT_CONTROLLER_PORT/$WEB_INTERFACE_FILE" 2>/dev/null &
    fi
}

stop_services() {
    echo -e "${BLUE}Stopping all services...${NC}"
    
    # Stop controller
    if [ -f "$CONTROLLER_PID_FILE" ]; then
        PID=$(cat "$CONTROLLER_PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo -e "${CYAN}Stopping controller (PID: $PID)...${NC}"
            kill $PID
            sleep 2
            if kill -0 $PID 2>/dev/null; then
                kill -9 $PID
            fi
        fi
        rm -f "$CONTROLLER_PID_FILE"
    fi
    
    # Stop Mininet
    if [ -f "$MININET_PID_FILE" ]; then
        echo -e "${CYAN}Stopping Mininet...${NC}"
        sudo mn -c > /dev/null 2>&1 || true
        rm -f "$MININET_PID_FILE"
    fi
    
    # Kill any remaining processes
    pkill -f "ryu-manager" 2>/dev/null || true
    pkill -f "flow_monitor_controller" 2>/dev/null || true
    pkill -f "mininet_client_controller" 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
}

show_status() {
    echo -e "${BLUE}System Status:${NC}"
    echo ""
    
    # Check root controller
    if [ -f "$CONTROLLER_PID_FILE" ] && kill -0 $(cat "$CONTROLLER_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}✅ Root Controller: Running (PID: $(cat $CONTROLLER_PID_FILE))${NC}"
        if curl -s "http://$ROOT_ADDRESS:$ROOT_CONTROLLER_PORT/stats" > /dev/null 2>&1; then
            echo -e "${GREEN}   REST API: Responding${NC}"
        else
            echo -e "${RED}   REST API: Not responding${NC}"
        fi
    else
        echo -e "${RED}❌ Root Controller: Not running${NC}"
    fi
    
    # Check client controller
    if curl -s "http://$CLIENT_ADDRESS:$CLIENT_CONTROLLER_PORT/stats" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Client Controller: Running and responding${NC}"
    else
        echo -e "${RED}❌ Client Controller: Not running or not responding${NC}"
    fi
    
    # Check Mininet
    if [ -f "$MININET_PID_FILE" ] && kill -0 $(cat "$MININET_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}✅ Mininet: Running (PID: $(cat $MININET_PID_FILE))${NC}"
    else
        echo -e "${RED}❌ Mininet: Not running${NC}"
    fi
    
    # Check network connectivity
    if ping -c 1 "$ROOT_ADDRESS" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Network: Root server reachable${NC}"
    else
        echo -e "${RED}❌ Network: Root server unreachable${NC}"
    fi
    
    if ping -c 1 "$CLIENT_ADDRESS" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Network: Client server reachable${NC}"
    else
        echo -e "${RED}❌ Network: Client server unreachable${NC}"
    fi
}

# Parse command line arguments
VERBOSE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --root-ip)
            ROOT_ADDRESS="$2"
            shift 2
            ;;
        --client-ip)
            CLIENT_ADDRESS="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            print_header
            print_usage
            exit 0
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Main script logic
print_header

case "${COMMAND:-}" in
    "root-start")
        check_dependencies
        start_root_controller
        ;;
    "client-start")
        check_dependencies
        start_client_controller
        ;;
    "mininet-start")
        start_mininet
        ;;
    "web")
        open_web_interface
        ;;
    "stop")
        stop_services
        ;;
    "status")
        show_status
        ;;
    "check-deps")
        check_dependencies
        ;;
    "logs")
        echo -e "${BLUE}Controller Logs:${NC}"
        if [ -f "logs/root_controller.log" ]; then
            echo -e "${CYAN}=== Root Controller Log ===${NC}"
            tail -20 logs/root_controller.log
        fi
        if [ -f "logs/client_controller.log" ]; then
            echo -e "${CYAN}=== Client Controller Log ===${NC}"
            tail -20 logs/client_controller.log
        fi
        ;;
    *)
        print_usage
        exit 1
        ;;
esac
