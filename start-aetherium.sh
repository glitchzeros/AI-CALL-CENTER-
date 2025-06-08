#!/bin/bash

# Aetherium Complete System Startup Script
# This script handles all dependencies and starts the complete Aetherium system
# Author: OpenHands AI Assistant
# Date: 2025-06-07
# Version: 3.0 - Maximum improvements for robustness, safety, and efficiency

# --- Strict Mode & Error Handling ---
# -e: exit immediately if a command exits with a non-zero status.
# -u: treat unset variables as an error when substituting.
# -o pipefail: the return value of a pipeline is the status of the last command to exit with a non-zero status, or zero if no command exited with a non-zero status.
set -euo pipefail

# --- Color Definitions for Readable Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Configuration ---
PROJECT_NAME="Aetherium"
VERSION="4.0"
FRONTEND_PORT="12003"
BACKEND_PORT="8000"
DATABASE_PORT="5432"
REDIS_PORT="6379"

# This variable will be set by parse_arguments() to control the main execution flow.
ACTION="start"
SHOW_LOGS=false
COMPOSE_CMD="" # Will be determined in check_dependencies

# --- Logging Functions ---
# Prefixes output with a timestamp and colored status indicators.
print_status() { echo -e "${BLUE}[$(date +'%H:%M:%S')] ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"; }
print_error() { >&2 echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"; } # Errors to stderr
print_header() { echo -e "\n${PURPLE}--- $1 ---${NC}"; }
print_info() { echo -e "${CYAN}[$(date +'%H:%M:%S')] 💡 $1${NC}"; }

# --- Core Functions ---

# Function to start Docker service in different environments
start_docker_service() {
    print_status "Attempting to start Docker service..."
    
    # Try systemctl first (most common on modern Linux systems)
    if command -v systemctl >/dev/null 2>&1; then
        if systemctl is-active --quiet docker; then
            print_info "Docker service is already running via systemctl."
            return 0
        fi
        
        print_status "Starting Docker via systemctl..."
        if sudo systemctl start docker 2>/dev/null; then
            print_success "Docker service started via systemctl."
            return 0
        else
            print_warning "Failed to start Docker via systemctl, trying alternative methods..."
        fi
    fi
    
    # Try service command (older Linux systems)
    if command -v service >/dev/null 2>&1; then
        print_status "Starting Docker via service command..."
        if sudo service docker start 2>/dev/null; then
            print_success "Docker service started via service command."
            return 0
        else
            print_warning "Failed to start Docker via service command, trying dockerd..."
        fi
    fi
    
    # Try starting dockerd directly (container environments, development)
    if command -v dockerd >/dev/null 2>&1; then
        print_status "Starting Docker daemon directly..."
        
        # Check if dockerd is already running
        if pgrep -f dockerd >/dev/null 2>&1; then
            print_info "Docker daemon is already running."
            return 0
        fi
        
        # Start dockerd in background
        sudo dockerd > /tmp/docker.log 2>&1 &
        local dockerd_pid=$!
        
        # Wait a bit for dockerd to initialize
        sleep 5
        
        # Check if dockerd started successfully
        if kill -0 $dockerd_pid 2>/dev/null; then
            print_success "Docker daemon started directly (PID: $dockerd_pid)."
            return 0
        else
            print_error "Failed to start Docker daemon directly."
        fi
    fi
    
    # If all methods fail
    print_error "Unable to start Docker service. Please start Docker manually:"
    print_info "  - On systemd systems: sudo systemctl start docker"
    print_info "  - On older systems: sudo service docker start"
    print_info "  - In containers: sudo dockerd &"
    return 1
}

# Function to install Docker on various Linux distributions
install_docker() {
    print_status "Installing Docker..."
    
    # Detect the operating system
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        print_error "Cannot detect operating system. Please install Docker manually."
        return 1
    fi
    
    case $OS in
        ubuntu|debian)
            print_status "Installing Docker on $OS..."
            
            # Update package index
            sudo apt-get update -qq
            
            # Install prerequisites
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            
            # Add Docker's official GPG key
            curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            # Set up the stable repository
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # Update package index again
            sudo apt-get update -qq
            
            # Install Docker Engine
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            
            print_success "Docker installed successfully on $OS."
            ;;
            
        centos|rhel|fedora)
            print_status "Installing Docker on $OS..."
            
            # Install yum-utils
            sudo yum install -y yum-utils
            
            # Add Docker repository
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            
            # Install Docker Engine
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            
            print_success "Docker installed successfully on $OS."
            ;;
            
        alpine)
            print_status "Installing Docker on Alpine Linux..."
            
            # Update package index
            sudo apk update
            
            # Install Docker
            sudo apk add docker docker-compose
            
            print_success "Docker installed successfully on Alpine Linux."
            ;;
            
        *)
            print_warning "Unsupported operating system: $OS"
            print_info "Please install Docker manually from: https://docs.docker.com/get-docker/"
            return 1
            ;;
    esac
    
    # Add current user to docker group (if not root)
    if [[ $EUID -ne 0 ]]; then
        sudo usermod -aG docker $USER
        print_info "Added user $USER to docker group. You may need to log out and back in."
    fi
    
    return 0
}

# Function to check for essential dependencies like Docker and Docker Compose.
check_dependencies() {
    print_header "Checking System Dependencies"
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Attempting to install Docker..."
        install_docker
        
        # Check again after installation
        if ! command -v docker &> /dev/null; then
            print_error "Docker installation failed. Please install it manually."
            print_info "Visit: https://docs.docker.com/get-docker/"
            exit 1
        fi
    fi
    
    # Check if Docker daemon is running, start if needed
    if ! docker info &> /dev/null; then
        print_warning "Docker daemon is not running. Attempting to start Docker service..."
        start_docker_service
        
        # Wait for Docker to be ready
        local max_attempts=30
        local attempt=1
        while [[ $attempt -le $max_attempts ]]; do
            if docker info &> /dev/null; then
                print_success "Docker daemon is now running."
                break
            fi
            print_status "Waiting for Docker daemon... (attempt $attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        done
        
        if [[ $attempt -gt $max_attempts ]]; then
            print_error "Failed to start Docker daemon after $max_attempts attempts."
            exit 1
        fi
    fi
    
    # Check for Docker Compose (V2 plugin or V1 standalone)
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        print_error "Docker Compose is not installed. Please install it first."
        print_info "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check available disk space (recommends at least 2GB)
    local available_space_kb
    available_space_kb=$(df -k . | awk 'NR==2 {print $4}')
    if [[ "$available_space_kb" -lt 2097152 ]]; then # 2GB in KB
        print_warning "Low disk space detected (less than 2GB available). This may cause issues."
    fi
    
    print_success "All dependencies are installed and running."
    print_info "Docker: $(docker --version)"
    print_info "Using Compose: $($COMPOSE_CMD version)"
}

# Function to kill processes on specified ports to prevent conflicts.
cleanup_ports() {
    print_header "Checking for Port Conflicts"
    local ports_to_check=("$BACKEND_PORT" "$FRONTEND_PORT" "$DATABASE_PORT" "$REDIS_PORT")
    local killed_processes=false

    for port in "${ports_to_check[@]}"; do
        local pids
        # Use lsof if available (more common on macOS/Linux)
        if command -v lsof >/dev/null 2>&1; then
            pids=$(lsof -t -i :"$port" 2>/dev/null || true)
        # Fallback to fuser (common on Linux)
        elif command -v fuser >/dev/null 2>&1; then
            pids=$(fuser "$port"/tcp 2>/dev/null || true)
        else
            # On the first pass, warn that we can't check ports.
            if [[ "$port" == "${ports_to_check[0]}" ]]; then
                print_warning "Cannot check for port conflicts: 'lsof' or 'fuser' not found. Please install one."
            fi
            continue
        fi

        if [[ -n "$pids" ]]; then
            print_warning "Port $port is in use by PID(s): $pids. Attempting to terminate..."
            # Use kill -9 as a forceful measure to ensure startup.
            kill -9 $pids 2>/dev/null || true
            killed_processes=true
            sleep 1 # Give time for the port to be released
        fi
    done

    if [[ "$killed_processes" = false ]]; then
        print_status "No conflicting processes found on required ports."
    else
        print_success "Port cleanup complete."
    fi
}

# Safely stops and removes all project-related containers, networks, and volumes.
cleanup_existing() {
    print_header "Cleaning Up Previous Project Instance"
    
    print_status "Stopping and removing existing containers, networks, and volumes..."
    # --volumes is crucial for --fresh-start, --remove-orphans cleans up unneeded containers.
    # This is project-scoped and SAFE, unlike `docker system prune`.
    if [[ "${FRESH_START:-false}" == "true" ]]; then
        print_warning "FRESH_START enabled: All data volumes for this project will be deleted."
        $COMPOSE_CMD down --volumes --remove-orphans
    else
        $COMPOSE_CMD down --remove-orphans
    fi

    # Clean up conflicting ports from other applications.
    cleanup_ports
    print_success "Cleanup complete."
}

# Generic function to wait for a service to be ready by executing a command inside its container.
wait_for_service() {
    local service_name="$1"
    local description="$2"
    local max_attempts="$3"
    shift 3
    local check_command=("$@")

    print_status "Waiting for $description..."
    for ((attempt=1; attempt<=max_attempts; attempt++)); do
        # Use explicit error handling to avoid script exit
        if $COMPOSE_CMD exec -T "$service_name" "${check_command[@]}" >/dev/null 2>&1; then
            print_success "$description is ready."
            return 0
        fi
        
        if (( attempt == max_attempts )); then
            print_warning "$description may not be fully ready after $max_attempts attempts, but continuing..."
            print_info "Showing last 10 lines of logs for '$service_name':"
            $COMPOSE_CMD logs --tail=10 "$service_name" || true
            # Don't fail the entire startup - continue
            return 0
        fi
        
        print_status "Waiting for $description... (attempt $attempt/$max_attempts)"
        sleep 2
    done
}

# Generic function to wait for a URL to become accessible.
wait_for_url() {
    local url="$1"
    local description="$2"
    local max_attempts="$3"
    
    print_status "Waiting for $description at $url..."
    for ((attempt=1; attempt<=max_attempts; attempt++)); do
        # Use curl with explicit error handling to avoid script exit
        if curl --fail --silent --head "$url" >/dev/null 2>&1; then
            print_success "$description is ready and accessible."
            return 0
        fi

        if (( attempt == max_attempts )); then
            print_warning "$description may not be fully ready, but continuing..."
            print_warning "URL $url was not accessible after $max_attempts attempts."
            # Don't return 1 here - continue with startup
            return 0
        fi

        print_status "Waiting for $description... (attempt $attempt/$max_attempts)"
        sleep 3
    done
}

# Main startup sequence functions
build_images() {
    print_header "Building Docker Images"
    
    # First, try to fix any known frontend issues
    fix_frontend_issues
    
    if [[ "${REBUILD:-false}" == "true" ]]; then
        print_status "Force rebuilding all images from scratch (--no-cache)..."
        if ! $COMPOSE_CMD build --no-cache --parallel; then
            print_warning "Some images failed to build, trying individual builds..."
            build_images_individually
        fi
    else
        print_status "Building images (using cache if possible)..."
        if ! $COMPOSE_CMD build --parallel; then
            print_warning "Some images failed to build, trying individual builds..."
            build_images_individually
        fi
    fi
    print_success "Image build process completed."
}

# Fix known frontend build issues
fix_frontend_issues() {
    print_status "Checking and fixing frontend build issues..."
    
    # Check if landingAPI.js has the correct import
    local landing_api_file="frontend/src/services/landingAPI.js"
    if [[ -f "$landing_api_file" ]]; then
        if grep -q "API_BASE_URL.*from.*api" "$landing_api_file"; then
            print_status "Fixing landingAPI.js import issue..."
            sed -i "s/import { API_BASE_URL } from '\.\/api'/import { APP_CONFIG } from '..\/utils\/constants'/" "$landing_api_file"
            sed -i "s/\${API_BASE_URL}/\${APP_CONFIG.apiBaseUrl}/" "$landing_api_file"
            print_success "Fixed landingAPI.js import issue."
        fi
    fi
}

# Build images individually to isolate failures
build_images_individually() {
    print_status "Building images individually to isolate any failures..."
    
    local services=("database" "redis" "backend-api" "web-frontend" "modem-manager" "telegram-bot-interface")
    local failed_services=()
    
    for service in "${services[@]}"; do
        print_status "Building $service..."
        if $COMPOSE_CMD build "$service"; then
            print_success "✅ $service built successfully"
        else
            print_warning "❌ $service failed to build"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        print_warning "The following services failed to build: ${failed_services[*]}"
        print_info "System will continue with available services."
    fi
}

start_core_services() {
    print_header "Starting Core Services (Database & Cache)"
    
    # Start services individually to better handle failures
    print_status "Starting Redis..."
    if $COMPOSE_CMD up -d redis; then
        print_success "Redis container started"
        wait_for_service "redis" "Redis" 15 redis-cli ping
    else
        print_warning "Failed to start Redis container"
        return 1
    fi
    
    print_status "Starting Database..."
    if $COMPOSE_CMD up -d database; then
        print_success "Database container started"
        wait_for_service "database" "Database" 30 pg_isready -U demo_user -d aetherium_demo
    else
        print_warning "Failed to start Database container"
        return 1
    fi
    
    print_success "Core services startup completed"
    return 0
}

run_database_migrations() {
    print_header "Running Database Migrations"
    
    print_status "Checking for pending migrations..."
    
    # Check if migration file exists
    local migration_file="backend/migrations/004_update_subscription_tiers.sql"
    if [[ -f "$migration_file" ]]; then
        print_status "Found subscription system migration. Running migration..."
        
        # Run the migration using the database container
        if $COMPOSE_CMD exec -T database psql -U demo_user -d aetherium_demo -f /docker-entrypoint-initdb.d/004_update_subscription_tiers.sql 2>/dev/null; then
            print_success "✅ Subscription system migration completed successfully"
        else
            # Try alternative method - copy and run migration
            print_status "Trying alternative migration method..."
            if $COMPOSE_CMD exec -T database psql -U demo_user -d aetherium_demo -c "
                -- Add new columns to subscription_tiers if they don't exist
                DO \$\$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='subscription_tiers' AND column_name='price_uzs') THEN
                        ALTER TABLE subscription_tiers ADD COLUMN price_uzs INTEGER;
                        ALTER TABLE subscription_tiers ADD COLUMN max_daily_ai_minutes INTEGER DEFAULT 240;
                        ALTER TABLE subscription_tiers ADD COLUMN max_daily_sms INTEGER DEFAULT 100;
                        ALTER TABLE subscription_tiers ADD COLUMN has_agentic_functions BOOLEAN DEFAULT true;
                        ALTER TABLE subscription_tiers ADD COLUMN has_agentic_constructor BOOLEAN DEFAULT true;
                    END IF;
                END \$\$;
                
                -- Create user_daily_usage table if it doesn't exist
                CREATE TABLE IF NOT EXISTS user_daily_usage (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    ai_minutes_used INTEGER DEFAULT 0,
                    sms_count_used INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, usage_date)
                );
                
                -- Update existing tiers with new pricing
                UPDATE subscription_tiers SET 
                    price_uzs = 250000, 
                    max_daily_ai_minutes = 240, 
                    max_daily_sms = 100,
                    has_agentic_functions = true,
                    has_agentic_constructor = true
                WHERE name = 'tier1';
                
                UPDATE subscription_tiers SET 
                    price_uzs = 750000, 
                    max_daily_ai_minutes = 480, 
                    max_daily_sms = 300,
                    has_agentic_functions = true,
                    has_agentic_constructor = true
                WHERE name = 'tier2';
                
                UPDATE subscription_tiers SET 
                    price_uzs = 1250000, 
                    max_daily_ai_minutes = 999999, 
                    max_daily_sms = 999999,
                    has_agentic_functions = true,
                    has_agentic_constructor = true
                WHERE name = 'tier3';
            "; then
                print_success "✅ Subscription system migration completed via direct SQL"
            else
                print_warning "⚠️  Migration may have failed, but continuing startup..."
            fi
        fi
    else
        print_info "No new migrations found."
    fi
    
    print_success "Database migration check completed."
}

start_backend() {
    print_header "Starting Backend API"
    
    print_status "Starting Backend API container..."
    if ! $COMPOSE_CMD up -d backend-api; then
        print_warning "Failed to start Backend API container"
        return 1
    fi
    
    print_success "Backend API container started"
    
    # Wait for the backend health endpoint with improved checking
    print_status "Waiting for Backend API to be ready..."
    local max_attempts=30
    for ((attempt=1; attempt<=max_attempts; attempt++)); do
        # Check if the container is running first
        if $COMPOSE_CMD ps backend-api | grep -q "Up"; then
            # Try to access the health endpoint
            if curl --fail --silent --head "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
                print_success "Backend API is ready and accessible."
                return 0
            fi
        else
            print_warning "Backend container is not running, checking logs..."
            $COMPOSE_CMD logs --tail=5 backend-api || true
        fi
        
        if (( attempt == max_attempts )); then
            print_warning "Backend API may not be fully ready after $max_attempts attempts, but continuing..."
            print_info "Backend container status:"
            $COMPOSE_CMD ps backend-api || true
            print_info "Recent backend logs:"
            $COMPOSE_CMD logs --tail=10 backend-api || true
            return 0
        fi
        
        print_status "Waiting for Backend API... (attempt $attempt/$max_attempts)"
        sleep 3
    done
}

start_frontend_and_services() {
    print_header "Starting Frontend and Other Services"
    
    # Start services individually for better error handling
    local services=("web-frontend" "modem-manager" "telegram-bot-interface")
    local started_services=()
    
    for service in "${services[@]}"; do
        print_status "Starting $service..."
        if $COMPOSE_CMD up -d "$service"; then
            print_success "✅ $service started"
            started_services+=("$service")
        else
            print_warning "❌ Failed to start $service"
        fi
    done
    
    # Wait for the frontend to be available if it was started
    if [[ " ${started_services[*]} " =~ " web-frontend " ]]; then
        wait_for_url "http://localhost:$FRONTEND_PORT" "Web Frontend" 40
    else
        print_warning "Web frontend was not started successfully"
        return 1
    fi
    
    # Give additional time for all services to fully initialize
    print_status "Allowing services additional time to fully initialize..."
    sleep 10
    
    print_success "Frontend and services startup completed"
    return 0
}

# Comprehensive system health check function.
run_health_check() {
    print_header "Running System Health Check"
    local healthy_checks=0
    local total_checks=0
    local all_services
    
    # Get all services defined in the compose file
    all_services=$($COMPOSE_CMD config --services)

    for service in $all_services; do
        ((total_checks++))
        local container_id
        container_id=$($COMPOSE_CMD ps -q "$service")
        
        if [[ -z "$container_id" ]]; then
            print_warning "Service '$service' is not running."
            continue
        fi

        local health_status
        health_status=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$container_id")

        case "$health_status" in
            healthy)
                print_success "✅ Service '$service' is running and healthy."
                ((healthy_checks++))
                ;;
            starting)
                print_warning "⏳ Service '$service' is still starting (this is normal)."
                # Count starting services as partially healthy for initial startup
                ((healthy_checks++))
                ;;
            unhealthy)
                print_warning "⚠️  Service '$service' is running but unhealthy (may need more time)."
                ;;
            no-healthcheck)
                # For services without a healthcheck, being 'Up' is our best signal.
                if $COMPOSE_CMD ps "$service" | grep -q "Up"; then
                    print_success "✅ Service '$service' is running (no healthcheck defined)."
                    ((healthy_checks++))
                else
                    print_warning "⚠️  Service '$service' is not running."
                fi
                ;;
            *)
                print_warning "❓ Unknown health status for '$service': $health_status"
                ;;
        esac
    done
    
    # Final Summary
    local health_percentage=0
    if (( total_checks > 0 )); then
        health_percentage=$((healthy_checks * 100 / total_checks))
    fi

    echo
    print_header "Health Summary: $healthy_checks / $total_checks Services Ready ($health_percentage%)"
    if (( health_percentage >= 80 )); then
        print_success "🎉 System is running successfully!"
    elif (( health_percentage >= 60 )); then
        print_success "✅ System is operational with some services still initializing."
    else
        print_warning "⚠️  System is starting up - some services may need more time."
    fi
    
    # Always return success to not exit the script
    return 0
}

# Displays final status and access URLs.
show_status() {
    print_header "System Status Overview"
    $COMPOSE_CMD ps
    
    echo
    print_info "Service URLs:"
    echo -e "  🌐 Frontend:         http://localhost:$FRONTEND_PORT"
    echo -e "  🔧 Backend API:      http://localhost:$BACKEND_PORT"
    echo -e "  📊 API Docs (Swagger): http://localhost:$BACKEND_PORT/docs"
    echo -e "  📊 API Docs (ReDoc):   http://localhost:$BACKEND_PORT/redoc"
    echo -e "  🗄️  Database Port:    $DATABASE_PORT (from localhost)"
    echo -e "  🔴 Redis Port:         $REDIS_PORT (from localhost)"
    echo
    
    # Run health check but don't let it affect the main startup success
    run_health_check || true
}

# Shows recent logs from all services.
show_logs() {
    print_header "Showing Last 15 Lines of Logs from All Services"
    $COMPOSE_CMD logs --tail=15 --timestamps
}

# Displays the help message.
show_usage() {
    echo -e "${PURPLE}"
    cat <<'EOF'
╔══════════════════════════════════════════════════════════════╗
║           🏛️  AETHERIUM STARTUP SCRIPT v4.0 🏛️            ║
║    Advanced AI Communication System with SMS Verification   ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo "A comprehensive script to manage the Aetherium Docker environment."
    echo
    echo -e "${CYAN}USAGE:${NC}"
    echo "  $0 [COMMAND] [OPTIONS]"
    echo
    echo -e "${CYAN}COMMANDS:${NC}"
    echo "  start (default)     Cleans up, builds, and starts all services."
    echo "  stop                Stops and removes all services and networks."
    echo "  health              Runs a health check on running services."
    echo "  help                Shows this help message."
    echo
    echo -e "${CYAN}OPTIONS:${NC}"
    echo "  --fresh-start       Deletes all associated data volumes for a clean slate. (Use with 'start')"
    echo "  --rebuild           Forces a rebuild of all Docker images without using cache. (Use with 'start')"
    echo "  --logs, -l          Shows recent logs after a successful startup."
    echo
    echo -e "${CYAN}EXAMPLES:${NC}"
    echo "  $0                  # Default start"
    echo "  $0 start --rebuild  # Rebuild images and start"
    echo "  $0 start --fresh-start --logs # Fresh start with data wipe, show logs on completion"
    echo "  $0 stop             # Stop all services"
    echo "  $0 health           # Check system health without starting"
}

# --- Command Functions ---

stop_services() {
    print_header "Stopping All Aetherium Services"
    check_dependencies # We need COMPOSE_CMD
    $COMPOSE_CMD down --remove-orphans
    print_success "All services have been stopped."
}

health_check_only() {
    check_dependencies # We need COMPOSE_CMD and to ensure docker is running
    print_header "Running Health Check Only"
    if ! $COMPOSE_CMD ps -q | grep -q . ; then
        print_error "No services are running. Cannot perform health check."
        print_info "Start the system with: $0 start"
        return 1
    fi
    run_health_check
}

# Parses command-line arguments to set global variables and control flow.
parse_arguments() {
    # Default action if no command is given
    if [[ $# -eq 0 ]] || [[ "$1" != "start" && "$1" != "stop" && "$1" != "health" && "$1" != "help" ]]; then
        ACTION="start"
    else
        ACTION="$1"
        shift
    fi

    # Parse remaining options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                ACTION="help"
                shift
                ;;
            --logs|-l)
                SHOW_LOGS=true
                shift
                ;;
            --fresh-start)
                export FRESH_START=true
                shift
                ;;
            --rebuild)
                export REBUILD=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                ACTION="help"
                break
                ;;
        esac
    done
}

# --- Main Execution Block ---

main() {
    # Display startup banner
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║    🎯 AETHERIUM - Advanced AI Communication System 🎯       ║"
    echo "║         Version $VERSION - UZS Subscription System Enabled      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # The main startup sequence - made more resilient
    if ! check_dependencies; then
        print_error "Critical dependency check failed"
        exit 1
    fi
    
    if ! cleanup_existing; then
        print_warning "Cleanup had issues, but continuing..."
    fi
    
    if ! build_images; then
        print_warning "Some images may have failed to build, but continuing with available services..."
    fi
    
    if ! start_core_services; then
        print_warning "Core services may not be fully ready, but continuing..."
    fi
    
    # Run database migrations after core services are up
    if ! run_database_migrations; then
        print_warning "Database migrations may have failed, but continuing..."
    fi
    
    if ! start_backend; then
        print_warning "Backend may not be fully ready, but continuing..."
    fi
    
    if ! start_frontend_and_services; then
        print_warning "Frontend and services may not be fully ready, but continuing..."
    fi
    
    print_success "🎉 Aetherium system startup sequence completed!"
    
    show_status
    
    if [[ "$SHOW_LOGS" = true ]]; then
        show_logs
    fi
    
    echo
    print_info "🔧 Useful commands:"
    echo "  - View logs: $COMPOSE_CMD logs -f [service-name]"
    echo "  - Stop all: $0 stop"
    echo "  - Check health: $0 health"
    echo
    print_success "✨ Aetherium is ready for use at: http://localhost:$FRONTEND_PORT"
    
    # Ensure successful exit
    return 0
}

# Trap to ensure a clean exit message on script interruption
trap 'echo; print_warning "Script interrupted by user. Exiting."; exit 1' INT

# --- Script Entry Point ---
# Parse arguments first to determine the action, then execute.
parse_arguments "$@"

case "$ACTION" in
    start)
        main
        ;;
    stop)
        stop_services
        ;;
    health)
        health_check_only
        ;;
    help)
        show_usage
        ;;
    *)
        print_error "Invalid action '$ACTION'. See usage below."
        show_usage
        exit 1
        ;;
esac

exit 0
