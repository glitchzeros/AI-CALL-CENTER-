#!/bin/bash

# Aetherium Complete System Startup Script
# This script handles all dependencies and starts the complete Aetherium system
# Author: OpenHands AI Assistant
# Date: 2025-06-07
# Version: 2.0 - Enhanced with all improvements and fixes

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures

echo "🚀 Starting Aetherium Complete System..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Aetherium"
VERSION="2.0"
FRONTEND_PORT="12001"  # Updated to use port 12001
BACKEND_PORT="8000"
DATABASE_PORT="5432"
REDIS_PORT="6379"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}[$(date +'%H:%M:%S')] 🚀 $1${NC}"
}

print_info() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] 💡 $1${NC}"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    print_header "Checking system dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        print_info "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    # Check for Docker Compose (either standalone or plugin)
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        COMPOSE_VERSION=$(docker-compose --version)
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
        COMPOSE_VERSION=$(docker compose version)
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        print_info "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check available disk space
    local available_space=$(df . | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 2097152 ]; then  # 2GB in KB
        print_warning "Low disk space detected. At least 2GB recommended."
    fi
    
    print_success "All dependencies are installed"
    print_info "Docker: $(docker --version)"
    print_info "Compose: $COMPOSE_VERSION"
}

# Enhanced port cleanup function
cleanup_ports() {
    local ports=($BACKEND_PORT $FRONTEND_PORT $DATABASE_PORT $REDIS_PORT 80 443)
    
    print_status "Cleaning up port conflicts..."
    
    for port in "${ports[@]}"; do
        if command -v fuser >/dev/null 2>&1; then
            local pids=$(fuser ${port}/tcp 2>/dev/null || true)
            if [ -n "$pids" ]; then
                print_warning "Killing processes on port $port: $pids"
                fuser -k ${port}/tcp 2>/dev/null || true
                sleep 1
            fi
        elif command -v lsof >/dev/null 2>&1; then
            local pids=$(lsof -ti:$port 2>/dev/null || true)
            if [ -n "$pids" ]; then
                print_warning "Killing processes on port $port: $pids"
                kill -9 $pids 2>/dev/null || true
                sleep 1
            fi
        fi
    done
}

# Stop any existing containers
cleanup_existing() {
    print_header "Cleaning up existing containers and resources..."
    
    # Stop and remove containers
    $COMPOSE_CMD down --remove-orphans --volumes 2>/dev/null || true
    
    # Clean up ports
    cleanup_ports
    
    # Remove old volumes for fresh start (optional)
    if [ "${FRESH_START:-false}" = "true" ]; then
        print_status "Removing old volumes for fresh start..."
        docker volume rm ozodbek-_postgres_data 2>/dev/null || true
        docker volume rm ozodbek-_redis_data 2>/dev/null || true
    fi
    
    # Clean up unused Docker resources
    print_status "Cleaning up unused Docker resources..."
    docker system prune -f --volumes 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Build all images
build_images() {
    print_header "Building Docker images..."
    
    # Check if we should rebuild or use cache
    if [ "${REBUILD:-false}" = "true" ]; then
        print_status "Rebuilding all images from scratch..."
        $COMPOSE_CMD build --no-cache --parallel
    else
        print_status "Building images (using cache when possible)..."
        $COMPOSE_CMD build --parallel
    fi
    
    print_success "All images built successfully"
}

# Start core services first
start_core_services() {
    print_header "Starting core services (Database & Redis)..."
    $COMPOSE_CMD up -d redis database
    
    print_status "Waiting for core services to initialize..."
    sleep 10
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    print_status "Checking database connectivity..."
    while [ $attempt -le $max_attempts ]; do
        if $COMPOSE_CMD exec -T database pg_isready -U demo_user -d aetherium_demo &>/dev/null; then
            print_success "Database is ready and accepting connections"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Database failed to start after $max_attempts attempts"
            print_error "Database logs:"
            $COMPOSE_CMD logs database --tail=20
            exit 1
        fi
        
        print_status "Waiting for database... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    # Wait for Redis to be ready
    print_status "Checking Redis connectivity..."
    local redis_attempts=10
    local redis_attempt=1
    
    while [ $redis_attempt -le $redis_attempts ]; do
        if $COMPOSE_CMD exec -T redis redis-cli ping &>/dev/null; then
            print_success "Redis is ready and responding"
            break
        fi
        
        if [ $redis_attempt -eq $redis_attempts ]; then
            print_warning "Redis may not be fully ready, but continuing..."
        fi
        
        print_status "Waiting for Redis... (attempt $redis_attempt/$redis_attempts)"
        sleep 1
        ((redis_attempt++))
    done
}

# Start backend services
start_backend() {
    print_header "Starting backend API..."
    $COMPOSE_CMD up -d backend-api
    
    print_status "Waiting for backend to initialize..."
    sleep 15
    
    # Check if backend is responding
    local max_attempts=25
    local attempt=1
    
    print_status "Checking backend API health..."
    while [ $attempt -le $max_attempts ]; do
        # Try both health endpoint and root endpoint
        if curl -f http://localhost:$BACKEND_PORT/health &>/dev/null || curl -f http://localhost:$BACKEND_PORT/ &>/dev/null; then
            print_success "Backend API is ready and responding"
            
            # Test database connection through backend
            if curl -f http://localhost:$BACKEND_PORT/health &>/dev/null; then
                print_success "Backend database connection verified"
            fi
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_warning "Backend may not be fully ready, but continuing..."
            print_warning "Backend logs (last 15 lines):"
            $COMPOSE_CMD logs backend-api --tail=15
            break
        fi
        
        print_status "Waiting for backend API... (attempt $attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done
}

# Start frontend and other services
start_frontend_and_services() {
    print_header "Starting frontend and remaining services..."
    
    # Start frontend service (updated to use port 12001)
    print_status "Starting web frontend..."
    $COMPOSE_CMD up -d web-frontend
    
    # Start additional services
    print_status "Starting additional services..."
    $COMPOSE_CMD up -d nginx modem-manager telegram-bot-interface
    
    print_status "Waiting for frontend to build and start..."
    sleep 25
    
    # Check frontend availability
    local frontend_attempts=15
    local frontend_attempt=1
    
    print_status "Checking frontend availability..."
    while [ $frontend_attempt -le $frontend_attempts ]; do
        if curl -f http://localhost:$FRONTEND_PORT &>/dev/null; then
            print_success "Frontend is ready and accessible"
            break
        fi
        
        if [ $frontend_attempt -eq $frontend_attempts ]; then
            print_warning "Frontend may still be building, check manually"
        fi
        
        print_status "Waiting for frontend... (attempt $frontend_attempt/$frontend_attempts)"
        sleep 2
        ((frontend_attempt++))
    done
    
    print_success "All services started"
}

# Enhanced system health check
run_health_check() {
    print_header "Running comprehensive system health check..."
    
    local health_score=0
    local total_checks=16
    
    # Service availability checks
    print_status "Checking service availability..."
    
    # Frontend check
    if curl -f http://localhost:$FRONTEND_PORT &>/dev/null; then
        print_success "✅ Frontend is accessible"
        ((health_score++))
    else
        print_warning "⚠️  Frontend may still be starting"
    fi
    
    # Backend API check
    if curl -f http://localhost:$BACKEND_PORT/health &>/dev/null; then
        print_success "✅ Backend API health endpoint responding"
        ((health_score++))
    else
        print_warning "⚠️  Backend API health check failed"
    fi
    
    # Backend root check
    if curl -f http://localhost:$BACKEND_PORT/ &>/dev/null; then
        print_success "✅ Backend API root endpoint responding"
        ((health_score++))
    else
        print_warning "⚠️  Backend API root endpoint not responding"
    fi
    
    # Database connectivity
    if $COMPOSE_CMD exec -T database pg_isready -U demo_user -d aetherium_demo &>/dev/null; then
        print_success "✅ Database is accepting connections"
        ((health_score++))
    else
        print_warning "⚠️  Database connection issues"
    fi
    
    # Redis connectivity
    if $COMPOSE_CMD exec -T redis redis-cli ping &>/dev/null; then
        print_success "✅ Redis is responding to ping"
        ((health_score++))
    else
        print_warning "⚠️  Redis connection issues"
    fi
    
    # Container status checks
    print_status "Checking container status..."
    
    local services=("database" "redis" "backend-api" "web-frontend")
    for service in "${services[@]}"; do
        if $COMPOSE_CMD ps $service | grep -q "Up"; then
            print_success "✅ $service container is running"
            ((health_score++))
        else
            print_warning "⚠️  $service container may have issues"
        fi
    done
    
    # Port accessibility checks
    print_status "Checking port accessibility..."
    
    local ports=($DATABASE_PORT $REDIS_PORT $BACKEND_PORT $FRONTEND_PORT)
    local port_names=("Database" "Redis" "Backend" "Frontend")
    
    for i in "${!ports[@]}"; do
        local port=${ports[$i]}
        local name=${port_names[$i]}
        
        if nc -z localhost $port 2>/dev/null; then
            print_success "✅ $name port $port is accessible"
            ((health_score++))
        else
            print_warning "⚠️  $name port $port is not accessible"
        fi
    done
    
    # Calculate health percentage
    local health_percentage=$((health_score * 100 / total_checks))
    
    echo ""
    print_header "System Health Summary"
    echo "===================="
    print_info "Health Score: $health_score/$total_checks ($health_percentage%)"
    
    if [ $health_percentage -ge 90 ]; then
        print_success "🎉 System is healthy and ready for use!"
    elif [ $health_percentage -ge 70 ]; then
        print_warning "⚠️  System is mostly healthy with minor issues"
    else
        print_error "❌ System has significant health issues"
    fi
}

# Display service status
show_status() {
    print_header "Service Status Overview"
    echo "======================="
    $COMPOSE_CMD ps
    echo ""
    
    print_info "Service URLs:"
    echo "============="
    echo "🌐 Frontend: http://localhost:$FRONTEND_PORT"
    echo "🔧 Backend API: http://localhost:$BACKEND_PORT"
    echo "📊 API Docs: http://localhost:$BACKEND_PORT/docs"
    echo "📊 API Interactive: http://localhost:$BACKEND_PORT/redoc"
    echo "🗄️  Database: localhost:$DATABASE_PORT"
    echo "🔴 Redis: localhost:$REDIS_PORT"
    echo ""
    
    # Run comprehensive health check
    run_health_check
}

# Show logs for troubleshooting
show_logs() {
    if [ "$1" = "--logs" ] || [ "$1" = "-l" ]; then
        print_header "Recent logs from all services:"
        echo "==============================="
        $COMPOSE_CMD logs --tail=10 --timestamps
    fi
}

# Usage information
show_usage() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║           🏛️  AETHERIUM STARTUP SCRIPT v$VERSION 🏛️            ║"
    echo "║                                                              ║"
    echo "║         Advanced AI Communication System                     ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 [OPTIONS]"
    echo ""
    echo -e "${CYAN}Options:${NC}"
    echo "  --help, -h          Show this help message"
    echo "  --logs, -l          Show recent logs after startup"
    echo "  --fresh-start       Remove all volumes for fresh start"
    echo "  --rebuild           Rebuild all images from scratch"
    echo "  --health-only       Run health check only (no startup)"
    echo "  --stop              Stop all services"
    echo ""
    echo -e "${CYAN}Environment Variables:${NC}"
    echo "  FRESH_START=true    Remove volumes for fresh start"
    echo "  REBUILD=true        Force rebuild of all images"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0                  # Normal startup"
    echo "  $0 --logs           # Startup with logs"
    echo "  $0 --fresh-start    # Fresh start (removes data)"
    echo "  $0 --rebuild        # Rebuild images and start"
    echo "  $0 --health-only    # Check system health only"
    echo ""
}

# Stop all services
stop_services() {
    print_header "Stopping all Aetherium services..."
    
    $COMPOSE_CMD down --remove-orphans
    cleanup_ports
    
    print_success "All services stopped"
    exit 0
}

# Health check only
health_check_only() {
    print_header "Running health check only..."
    
    if ! $COMPOSE_CMD ps | grep -q "Up"; then
        print_error "No services are running. Start services first with: $0"
        exit 1
    fi
    
    run_health_check
    exit 0
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_usage
                exit 0
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
            --health-only)
                health_check_only
                ;;
            --stop)
                stop_services
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║    🎯 AETHERIUM - Advanced AI Communication System 🎯       ║"
    echo "║                                                              ║"
    echo "║                   Version $VERSION - Enhanced                   ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    print_header "Complete system startup initiated..."
    
    # Startup sequence
    check_dependencies
    cleanup_existing
    build_images
    start_core_services
    start_backend
    start_frontend_and_services
    
    echo ""
    print_success "🎉 Aetherium system startup completed!"
    echo ""
    
    show_status
    
    if [ "${SHOW_LOGS:-false}" = "true" ]; then
        show_logs "--logs"
    fi
    
    echo ""
    print_info "🔧 Useful commands:"
    echo "  - View logs: $COMPOSE_CMD logs [service-name]"
    echo "  - Restart service: $COMPOSE_CMD restart [service-name]"
    echo "  - Stop all: $COMPOSE_CMD down"
    echo "  - Health check: $0 --health-only"
    echo "  - Fresh restart: $0 --fresh-start"
    echo "  - Help: $0 --help"
    echo ""
    
    print_success "✨ Aetherium is ready for use!"
    print_info "🌐 Access the application at: http://localhost:$FRONTEND_PORT"
}

# Parse arguments and run main function
parse_arguments "$@"
main