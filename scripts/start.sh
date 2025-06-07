#!/bin/bash

# Aetherium Start Script
# The Scribe's Awakening Ritual

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT=${ENVIRONMENT:-production}
COMPOSE_FILE="docker-compose.yml"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev|--development)
            ENVIRONMENT="development"
            COMPOSE_FILE="docker-compose.yml -f docker-compose.dev.yml"
            shift
            ;;
        --prod|--production)
            ENVIRONMENT="production"
            COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"
            shift
            ;;
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --detach|-d)
            DETACH_FLAG="-d"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dev, --development    Start in development mode"
            echo "  --prod, --production    Start in production mode (default)"
            echo "  --build                 Rebuild images before starting"
            echo "  --detach, -d           Run in detached mode"
            echo "  --help, -h             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Logging functions
log() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if .env file exists
check_env_file() {
    if [[ ! -f .env ]]; then
        error ".env file not found!"
        echo "Please run ./scripts/setup.sh first to create the environment file"
        exit 1
    fi
    
    # Load environment variables
    source .env
}

# Check Docker and Docker Compose
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
}

# Check system resources
check_resources() {
    log "Checking system resources..."
    
    # Check available memory (minimum 4GB)
    available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    required_memory=4096
    
    if [[ $available_memory -lt $required_memory ]]; then
        warning "Low available memory: ${available_memory}MB (recommended: ${required_memory}MB)"
    fi
    
    # Check available disk space (minimum 5GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    required_space=5242880  # 5GB in KB
    
    if [[ $available_space -lt $required_space ]]; then
        warning "Low available disk space: $(($available_space / 1024))MB (recommended: 5GB)"
    fi
}

# Stop existing containers
stop_existing() {
    log "Stopping existing containers..."
    
    if docker-compose ps -q | grep -q .; then
        docker-compose down
        success "Existing containers stopped"
    else
        log "No existing containers to stop"
    fi
}

# Pull latest images (for production)
pull_images() {
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log "Pulling latest images..."
        docker-compose -f $COMPOSE_FILE pull
        success "Images pulled successfully"
    fi
}

# Start services
start_services() {
    log "Starting Aetherium services in $ENVIRONMENT mode..."
    
    # Build command
    cmd="docker-compose -f $COMPOSE_FILE up"
    
    if [[ -n "$BUILD_FLAG" ]]; then
        cmd="$cmd --build"
    fi
    
    if [[ -n "$DETACH_FLAG" ]]; then
        cmd="$cmd -d"
    fi
    
    # Execute command
    eval $cmd
    
    if [[ -n "$DETACH_FLAG" ]]; then
        success "Services started in detached mode"
    fi
}

# Wait for services to be healthy
wait_for_services() {
    if [[ -n "$DETACH_FLAG" ]]; then
        log "Waiting for services to be healthy..."
        
        services=("database" "redis" "backend-api")
        max_wait=120
        wait_time=0
        
        for service in "${services[@]}"; do
            log "Waiting for $service to be healthy..."
            
            while ! docker-compose ps | grep "$service" | grep -q "healthy\|Up"; do
                sleep 5
                wait_time=$((wait_time + 5))
                
                if [[ $wait_time -ge $max_wait ]]; then
                    error "Service $service failed to start within ${max_wait} seconds"
                    show_logs
                    exit 1
                fi
            done
            
            success "$service is healthy"
        done
        
        success "All core services are healthy"
    fi
}

# Show service status
show_status() {
    if [[ -n "$DETACH_FLAG" ]]; then
        echo ""
        log "Service Status:"
        docker-compose ps
        
        echo ""
        log "Service URLs:"
        echo -e "${BLUE}• Web Interface:${NC} http://localhost:${FRONTEND_PORT:-12000}"
        echo -e "${BLUE}• API Documentation:${NC} http://localhost:${BACKEND_PORT:-8000}/docs"
        echo -e "${BLUE}• API Health Check:${NC} http://localhost:${BACKEND_PORT:-8000}/health"
        
        if [[ "$ENVIRONMENT" == "development" ]]; then
            echo -e "${BLUE}• PgAdmin:${NC} http://localhost:5050"
            echo -e "${BLUE}• Redis Commander:${NC} http://localhost:8081"
            echo -e "${BLUE}• MailHog:${NC} http://localhost:8025"
        fi
        
        if [[ "$ENVIRONMENT" == "production" ]]; then
            echo -e "${BLUE}• Grafana:${NC} http://localhost:3000"
            echo -e "${BLUE}• Prometheus:${NC} http://localhost:9090"
        fi
    fi
}

# Show logs on error
show_logs() {
    echo ""
    error "Service startup failed. Recent logs:"
    docker-compose logs --tail=20
}

# Cleanup on exit
cleanup() {
    if [[ $? -ne 0 ]]; then
        error "Startup failed!"
        show_logs
    fi
}

# Main function
main() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  🚀 STARTING AETHERIUM 🚀                   ║"
    echo "║              The Scribe's Awakening Begins...               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log "Environment: $ENVIRONMENT"
    log "Compose files: $COMPOSE_FILE"
    
    # Set up error handling
    trap cleanup EXIT
    
    # Run startup sequence
    check_env_file
    check_docker
    check_resources
    stop_existing
    pull_images
    start_services
    wait_for_services
    show_status
    
    if [[ -n "$DETACH_FLAG" ]]; then
        echo ""
        echo -e "${GREEN}"
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║                🎉 AETHERIUM IS RUNNING! 🎉                  ║"
        echo "║              The Scribe Awaits Your Command                 ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
        
        echo ""
        echo -e "${CYAN}Useful commands:${NC}"
        echo "• View logs: ${YELLOW}./scripts/logs.sh${NC}"
        echo "• Stop services: ${YELLOW}./scripts/stop.sh${NC}"
        echo "• Restart services: ${YELLOW}./scripts/restart.sh${NC}"
        echo "• Check status: ${YELLOW}docker-compose ps${NC}"
        echo ""
        echo -e "${PURPLE}May your conversations flow like ink upon parchment! ✨${NC}"
    fi
}

# Run main function
main "$@"