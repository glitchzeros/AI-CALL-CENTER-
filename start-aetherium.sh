#!/bin/bash

# Aetherium Complete System Startup Script
# This script handles all dependencies and starts the complete Aetherium system
# Author: OpenHands AI Assistant
# Date: 2025-06-07

set -e  # Exit on any error

echo "🚀 Starting Aetherium Complete System..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    print_status "Checking system dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check for Docker Compose (either standalone or plugin)
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "All dependencies are installed (using $COMPOSE_CMD)"
}

# Stop any existing containers
cleanup_existing() {
    print_status "Cleaning up existing containers..."
    $COMPOSE_CMD down --remove-orphans 2>/dev/null || true
    
    # Remove old volumes if they exist to ensure fresh start
    print_status "Removing old database volume for fresh start..."
    docker volume rm ozodbek-_postgres_data 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Build all images
build_images() {
    print_status "Building Docker images..."
    $COMPOSE_CMD build --no-cache
    print_success "All images built successfully"
}

# Start core services first
start_core_services() {
    print_status "Starting core services (Database & Redis)..."
    $COMPOSE_CMD up -d redis database
    
    print_status "Waiting for core services to be healthy..."
    sleep 10
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if $COMPOSE_CMD exec -T database pg_isready -U demo_user -d aetherium_demo &>/dev/null; then
            print_success "Database is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Database failed to start after $max_attempts attempts"
            $COMPOSE_CMD logs database
            exit 1
        fi
        
        print_status "Waiting for database... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
}

# Start backend services
start_backend() {
    print_status "Starting backend API..."
    $COMPOSE_CMD up -d backend-api
    
    print_status "Waiting for backend to be ready..."
    sleep 15
    
    # Check if backend is responding
    local max_attempts=20
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health &>/dev/null; then
            print_success "Backend API is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_warning "Backend may not be fully ready, but continuing..."
            print_status "Backend logs:"
            $COMPOSE_CMD logs backend-api --tail=10
            break
        fi
        
        print_status "Waiting for backend API... (attempt $attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done
}

# Start frontend and other services
start_frontend_and_services() {
    print_status "Starting frontend and remaining services..."
    $COMPOSE_CMD up -d web-frontend nginx modem-manager telegram-bot-interface
    
    print_status "Waiting for frontend to build and start..."
    sleep 20
    
    print_success "All services started"
}

# Display service status
show_status() {
    print_status "Service Status:"
    echo "==============="
    $COMPOSE_CMD ps
    echo ""
    
    print_status "Service URLs:"
    echo "============="
    echo "🌐 Frontend: http://localhost:12000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
    echo "🗄️  Database: localhost:5432"
    echo "🔴 Redis: localhost:6379"
    echo ""
    
    print_status "Service Health Check:"
    echo "===================="
    
    # Check frontend
    if curl -f http://localhost:12000 &>/dev/null; then
        print_success "✅ Frontend is accessible"
    else
        print_warning "⚠️  Frontend may still be starting"
    fi
    
    # Check backend
    if curl -f http://localhost:8000/health &>/dev/null; then
        print_success "✅ Backend API is accessible"
    else
        print_warning "⚠️  Backend API may have issues"
    fi
    
    # Check database
    if $COMPOSE_CMD exec -T database pg_isready -U demo_user -d aetherium_demo &>/dev/null; then
        print_success "✅ Database is accessible"
    else
        print_warning "⚠️  Database connection issues"
    fi
}

# Show logs for troubleshooting
show_logs() {
    if [ "$1" = "--logs" ] || [ "$1" = "-l" ]; then
        print_status "Recent logs from all services:"
        echo "==============================="
        $COMPOSE_CMD logs --tail=5
    fi
}

# Main execution
main() {
    echo "🎯 Aetherium - Advanced AI Communication System"
    echo "💫 Complete system startup initiated..."
    echo ""
    
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
    show_logs "$1"
    
    echo ""
    print_status "🔧 Troubleshooting commands:"
    echo "  - View logs: $COMPOSE_CMD logs [service-name]"
    echo "  - Restart service: $COMPOSE_CMD restart [service-name]"
    echo "  - Stop all: $COMPOSE_CMD down"
    echo "  - Full restart: ./start-aetherium.sh"
    echo ""
    print_success "✨ Aetherium is ready for use!"
}

# Run main function with all arguments
main "$@"