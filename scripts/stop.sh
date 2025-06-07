#!/bin/bash

# Aetherium Stop Script
# The Scribe's Rest Ritual

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse command line arguments
REMOVE_VOLUMES=false
REMOVE_IMAGES=false
FORCE_STOP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --volumes|-v)
            REMOVE_VOLUMES=true
            shift
            ;;
        --images|-i)
            REMOVE_IMAGES=true
            shift
            ;;
        --force|-f)
            FORCE_STOP=true
            shift
            ;;
        --all|-a)
            REMOVE_VOLUMES=true
            REMOVE_IMAGES=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --volumes, -v          Remove volumes (WARNING: This will delete all data!)"
            echo "  --images, -i           Remove images"
            echo "  --force, -f            Force stop containers"
            echo "  --all, -a              Remove volumes and images"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     Stop services (keep data)"
            echo "  $0 --force             Force stop all containers"
            echo "  $0 --volumes           Stop and remove all data"
            echo "  $0 --all               Stop and remove everything"
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

# Confirm destructive actions
confirm_action() {
    local message="$1"
    echo -e "${YELLOW}$message${NC}"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Operation cancelled"
        exit 0
    fi
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
}

# Stop containers
stop_containers() {
    log "Stopping Aetherium containers..."
    
    if docker-compose ps -q | grep -q .; then
        if [[ "$FORCE_STOP" == true ]]; then
            log "Force stopping containers..."
            docker-compose kill
        else
            log "Gracefully stopping containers..."
            docker-compose stop
        fi
        success "Containers stopped"
    else
        log "No running containers found"
    fi
}

# Remove containers
remove_containers() {
    log "Removing containers..."
    
    if docker-compose ps -a -q | grep -q .; then
        docker-compose rm -f
        success "Containers removed"
    else
        log "No containers to remove"
    fi
}

# Remove volumes
remove_volumes() {
    if [[ "$REMOVE_VOLUMES" == true ]]; then
        confirm_action "⚠️  WARNING: This will permanently delete all data including databases, logs, and uploads!"
        
        log "Removing volumes..."
        
        # Get volume names
        volumes=$(docker volume ls -q | grep aetherium || true)
        
        if [[ -n "$volumes" ]]; then
            echo "$volumes" | xargs docker volume rm
            success "Volumes removed"
        else
            log "No volumes to remove"
        fi
        
        # Remove local data directories
        if [[ -d "backend/logs" ]]; then
            rm -rf backend/logs/*
            log "Cleared backend logs"
        fi
        
        if [[ -d "modem-manager/logs" ]]; then
            rm -rf modem-manager/logs/*
            log "Cleared modem manager logs"
        fi
        
        if [[ -d "telegram-bot/logs" ]]; then
            rm -rf telegram-bot/logs/*
            log "Cleared telegram bot logs"
        fi
    fi
}

# Remove images
remove_images() {
    if [[ "$REMOVE_IMAGES" == true ]]; then
        log "Removing Aetherium images..."
        
        # Get image names
        images=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep aetherium || true)
        
        if [[ -n "$images" ]]; then
            echo "$images" | tail -n +2 | xargs docker rmi -f
            success "Images removed"
        else
            log "No Aetherium images to remove"
        fi
        
        # Remove dangling images
        dangling=$(docker images -f "dangling=true" -q)
        if [[ -n "$dangling" ]]; then
            echo "$dangling" | xargs docker rmi
            log "Removed dangling images"
        fi
    fi
}

# Remove networks
remove_networks() {
    log "Removing networks..."
    
    networks=$(docker network ls --format "{{.Name}}" | grep aetherium || true)
    
    if [[ -n "$networks" ]]; then
        echo "$networks" | xargs docker network rm 2>/dev/null || true
        success "Networks removed"
    else
        log "No networks to remove"
    fi
}

# Clean up system
cleanup_system() {
    if [[ "$REMOVE_IMAGES" == true ]]; then
        log "Cleaning up Docker system..."
        docker system prune -f
        success "System cleanup completed"
    fi
}

# Show final status
show_status() {
    echo ""
    log "Final Status:"
    
    # Check for remaining containers
    remaining_containers=$(docker ps -a --format "table {{.Names}}" | grep aetherium || true)
    if [[ -n "$remaining_containers" ]]; then
        warning "Remaining containers:"
        echo "$remaining_containers"
    else
        success "No Aetherium containers remaining"
    fi
    
    # Check for remaining volumes
    if [[ "$REMOVE_VOLUMES" == false ]]; then
        remaining_volumes=$(docker volume ls -q | grep aetherium || true)
        if [[ -n "$remaining_volumes" ]]; then
            log "Data volumes preserved:"
            echo "$remaining_volumes" | sed 's/^/  • /'
        fi
    fi
    
    # Check for remaining images
    if [[ "$REMOVE_IMAGES" == false ]]; then
        remaining_images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep aetherium || true)
        if [[ -n "$remaining_images" ]]; then
            log "Images preserved:"
            echo "$remaining_images" | sed 's/^/  • /'
        fi
    fi
}

# Main function
main() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  🌙 STOPPING AETHERIUM 🌙                   ║"
    echo "║               The Scribe Prepares to Rest...                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Show what will be done
    log "Stopping Aetherium services..."
    if [[ "$FORCE_STOP" == true ]]; then
        warning "Force stop enabled - containers will be killed immediately"
    fi
    if [[ "$REMOVE_VOLUMES" == true ]]; then
        warning "Volume removal enabled - all data will be deleted!"
    fi
    if [[ "$REMOVE_IMAGES" == true ]]; then
        warning "Image removal enabled - images will be deleted"
    fi
    
    # Run stop sequence
    check_docker
    stop_containers
    remove_containers
    remove_volumes
    remove_images
    remove_networks
    cleanup_system
    show_status
    
    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 🛌 AETHERIUM STOPPED 🛌                     ║"
    echo "║                The Scribe Rests Peacefully                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo ""
    echo -e "${CYAN}To start Aetherium again:${NC}"
    echo "  ${YELLOW}./scripts/start.sh${NC}"
    echo ""
    
    if [[ "$REMOVE_VOLUMES" == true ]]; then
        echo -e "${RED}⚠️  All data has been permanently deleted!${NC}"
        echo -e "${CYAN}To restore from backup:${NC}"
        echo "  ${YELLOW}./scripts/restore.sh${NC}"
        echo ""
    fi
    
    echo -e "${PURPLE}Until we meet again in the digital realm... ✨${NC}"
}

# Run main function
main "$@"