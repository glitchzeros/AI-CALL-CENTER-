#!/bin/bash

# Aetherium AI Call Center Platform
# Single Command Startup Script
# "The Scribe Awakens"

set -e

echo "🌟 ========================================"
echo "🌟 AETHERIUM - AI CALL CENTER PLATFORM"
echo "🌟 The Scribe's Awakening Sequence"
echo "🌟 ========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your actual configuration values"
        print_warning "Required: GEMINI_API_KEY, CLICK_API_KEY, TELEGRAM_BOT_TOKEN, etc."
        echo ""
        read -p "Press Enter to continue after configuring .env file..."
    else
        print_error ".env.example file not found. Please create .env manually."
        exit 1
    fi
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

print_header "📋 Pre-flight Checks"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker and Docker Compose are available"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker first."
    exit 1
fi

print_success "Docker daemon is running"

# Check for required environment variables
required_vars=("GEMINI_API_KEY" "JWT_SECRET_KEY" "POSTGRES_PASSWORD")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    print_error "Please configure these in your .env file"
    exit 1
fi

print_success "Required environment variables are set"

print_header "🏗️  Building Aetherium Services"

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs
mkdir -p audio_temp
mkdir -p uploads
mkdir -p static

# Build and start services
print_status "Building Docker images..."
docker-compose build --parallel

print_header "🚀 Starting Aetherium Platform"

# Start services
print_status "Starting all services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to initialize..."

# Function to wait for service
wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within expected time"
    return 1
}

# Wait for database
print_status "Waiting for database..."
sleep 10

# Wait for backend API
wait_for_service "Backend API" "http://localhost:8000/health"

# Wait for frontend
wait_for_service "Frontend" "http://localhost:12000"

# Wait for modem manager
wait_for_service "Modem Manager" "http://localhost:8001/health"

print_header "🔍 System Status Check"

# Check service status
print_status "Checking service status..."

services=("aetherium_database" "aetherium_backend" "aetherium_frontend" "aetherium_modem_manager" "aetherium_telegram_bot")

all_healthy=true
for service in "${services[@]}"; do
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$service.*Up"; then
        print_success "$service is running"
    else
        print_error "$service is not running properly"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    print_header "✅ Aetherium Platform Successfully Deployed!"
    echo ""
    echo -e "${CYAN}🌐 Access Points:${NC}"
    echo -e "   Web Portal: ${GREEN}http://localhost:12000${NC}"
    echo -e "   Backend API: ${GREEN}http://localhost:8000${NC}"
    echo -e "   API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "   Modem Manager: ${GREEN}http://localhost:8001${NC}"
    echo ""
    echo -e "${CYAN}📊 Service Status:${NC}"
    docker-compose ps
    echo ""
    echo -e "${PURPLE}🎭 The Scribe Awaits Your Command${NC}"
    echo -e "${YELLOW}\"Where AI Scribes dwell and conversations flow like ink upon parchment\"${NC}"
    echo ""
    echo -e "${CYAN}📝 Next Steps:${NC}"
    echo "1. Visit http://localhost:12000 to access the web portal"
    echo "2. Create an account and verify your phone number"
    echo "3. Choose a subscription tier"
    echo "4. Configure your Scribe's behavior in the Invocation Editor"
    echo "5. Start receiving calls on your assigned Company Number"
    echo ""
    echo -e "${CYAN}🔧 Management Commands:${NC}"
    echo "   View logs: docker-compose logs -f [service_name]"
    echo "   Stop platform: docker-compose down"
    echo "   Restart service: docker-compose restart [service_name]"
    echo "   Update platform: git pull && docker-compose build && docker-compose up -d"
    echo ""
else
    print_error "Some services failed to start properly. Check logs with:"
    echo "docker-compose logs"
    exit 1
fi