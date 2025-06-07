#!/bin/bash

# Aetherium Docker Setup Script
# Automatically sets up and runs the full project with Docker

set -e

echo "🏛️ Aetherium Docker Setup"
echo "=========================="

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Installing Docker..."
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    print_success "Docker installed successfully"
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_status "Starting Docker daemon..."
    
    # Try to start Docker daemon
    if command -v systemctl &> /dev/null; then
        sudo systemctl start docker
    else
        # For environments without systemd
        sudo dockerd > /tmp/docker.log 2>&1 &
        sleep 5
    fi
    
    print_success "Docker daemon started"
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing docker-compose..."
    
    # Install docker-compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "docker-compose installed"
fi

# Setup environment configuration
print_status "Setting up environment configuration..."
python3 scripts/setup_environment.py

# Copy generated environment file
if [ -f ".env.generated" ]; then
    cp .env.generated .env
    print_success "Environment file configured"
else
    print_warning "Using existing .env file"
fi

# Build and start services
print_status "Building and starting Docker services..."

# Stop any existing containers
docker-compose down 2>/dev/null || true

# Build and start services
if [ "$1" = "dev" ]; then
    print_status "Starting in development mode..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
else
    print_status "Starting in production mode..."
    docker-compose up --build -d
fi

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check service status
print_status "Checking service status..."

services=("database" "redis" "backend-api" "web-frontend")
for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        print_success "$service is running"
    else
        print_warning "$service may not be running properly"
    fi
done

# Display access information
echo ""
echo "🚀 Aetherium is now running!"
echo "=========================="
echo ""
echo "📱 Frontend (Admin Dashboard): http://localhost:12000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🗄️ Database: localhost:5432"
echo "🔴 Redis: localhost:6379"
echo ""
echo "🔍 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"
echo ""

# Show configuration status
print_status "Configuration Status:"
python3 -c "
from config.environment import get_config
config = get_config()
print(f'   Mode: {\"Demo\" if config.is_demo_mode() else \"Production\"}')
print(f'   Real values: {len(config.get_real_keys())}')
print(f'   Demo values: {len(config.get_demo_keys())}')
"

print_success "Setup complete! 🎉"