#!/bin/bash

# Aetherium Setup Script
# The Scribe's Initialization Ritual

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
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

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    required_space=10485760  # 10GB in KB
    
    if [[ $available_space -lt $required_space ]]; then
        error "Insufficient disk space. At least 10GB is required."
        exit 1
    fi
    
    success "System requirements check passed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    directories=(
        "backend/logs"
        "backend/uploads"
        "backend/static"
        "frontend/dist"
        "modem-manager/logs"
        "telegram-bot/logs"
        "docker/ssl"
        "monitoring"
        "backups"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log "Created directory: $dir"
    done
    
    success "Directories created successfully"
}

# Setup environment files
setup_environment() {
    log "Setting up environment configuration..."
    
    if [[ ! -f .env ]]; then
        if [[ -f .env.example ]]; then
            cp .env.example .env
            log "Created .env from .env.example"
        else
            create_default_env
        fi
    else
        warning ".env file already exists, skipping creation"
    fi
    
    # Generate secure secrets if not set
    if ! grep -q "JWT_SECRET_KEY=" .env || grep -q "JWT_SECRET_KEY=$" .env; then
        jwt_secret=$(openssl rand -hex 32)
        sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$jwt_secret/" .env
        log "Generated JWT secret key"
    fi
    
    if ! grep -q "ENCRYPTION_KEY=" .env || grep -q "ENCRYPTION_KEY=$" .env; then
        encryption_key=$(openssl rand -hex 32)
        sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$encryption_key/" .env
        log "Generated encryption key"
    fi
    
    success "Environment configuration completed"
}

# Create default .env file
create_default_env() {
    cat > .env << EOF
# Aetherium Environment Configuration

# Database
POSTGRES_PASSWORD=aetherium_secure_pass_$(date +%Y)
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
BACKEND_PORT=8000
FRONTEND_PORT=12000

# Security
JWT_SECRET_KEY=
ENCRYPTION_KEY=

# External APIs
GEMINI_API_KEY=
TELEGRAM_BOT_TOKEN=

# Payment Information
COMPANY_BANK_CARD=
COMPANY_BANK_NAME=
COMPANY_CARDHOLDER_NAME=
COMPANY_BANK_PHONE=

# SSL (for production)
DOMAIN_NAME=
SSL_EMAIL=

# Monitoring
GRAFANA_PASSWORD=admin123

# CORS
CORS_ORIGINS=*

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
EOF
    log "Created default .env file"
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Backend dependencies
    if [[ -f backend/requirements.txt ]]; then
        log "Backend Python dependencies will be installed in Docker container"
    fi
    
    # Frontend dependencies
    if [[ -f frontend/package.json ]]; then
        if command -v npm &> /dev/null; then
            log "Installing frontend dependencies..."
            cd frontend
            npm install
            cd ..
            success "Frontend dependencies installed"
        else
            warning "npm not found, frontend dependencies will be installed in Docker container"
        fi
    fi
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    # Check if database is already running
    if docker ps | grep -q aetherium_database; then
        warning "Database container is already running"
        return
    fi
    
    # Start database container
    docker-compose up -d database
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    timeout=60
    while ! docker exec aetherium_database pg_isready -U aetherium_user -d aetherium &> /dev/null; do
        sleep 2
        timeout=$((timeout - 2))
        if [[ $timeout -le 0 ]]; then
            error "Database failed to start within 60 seconds"
            exit 1
        fi
    done
    
    success "Database is ready"
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    # Build all images
    docker-compose build --parallel
    
    success "Docker images built successfully"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring configuration..."
    
    # Create Prometheus config
    mkdir -p monitoring
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'aetherium-backend'
    static_configs:
      - targets: ['backend-api:8000']
    metrics_path: '/metrics'

  - job_name: 'aetherium-frontend'
    static_configs:
      - targets: ['web-frontend:80']

  - job_name: 'postgres'
    static_configs:
      - targets: ['database:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
    
    success "Monitoring configuration created"
}

# Setup SSL certificates (for production)
setup_ssl() {
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log "Setting up SSL certificates..."
        
        if [[ -z "$DOMAIN_NAME" ]]; then
            warning "DOMAIN_NAME not set in .env, skipping SSL setup"
            return
        fi
        
        # Create SSL directory
        mkdir -p docker/ssl
        
        # Generate self-signed certificate for development
        if [[ ! -f docker/ssl/cert.pem ]]; then
            openssl req -x509 -newkey rsa:4096 -keyout docker/ssl/key.pem -out docker/ssl/cert.pem -days 365 -nodes \
                -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN_NAME"
            log "Generated self-signed SSL certificate"
        fi
        
        success "SSL setup completed"
    fi
}

# Validate configuration
validate_config() {
    log "Validating configuration..."
    
    # Check required environment variables
    required_vars=(
        "POSTGRES_PASSWORD"
        "JWT_SECRET_KEY"
        "ENCRYPTION_KEY"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" .env || grep -q "^$var=$" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        error "Missing required environment variables: ${missing_vars[*]}"
        echo "Please update your .env file with the required values"
        exit 1
    fi
    
    # Validate Docker Compose files
    if ! docker-compose config &> /dev/null; then
        error "Docker Compose configuration is invalid"
        exit 1
    fi
    
    success "Configuration validation passed"
}

# Main setup function
main() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🌟 AETHERIUM SETUP 🌟                    ║"
    echo "║              Where AI Scribes Dwell and Flourish            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log "Starting Aetherium setup process..."
    
    # Load environment if exists
    if [[ -f .env ]]; then
        source .env
    fi
    
    # Run setup steps
    check_root
    check_requirements
    create_directories
    setup_environment
    install_dependencies
    setup_monitoring
    setup_ssl
    validate_config
    setup_database
    build_images
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   🎉 SETUP COMPLETED! 🎉                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "1. Update your .env file with your API keys and configuration"
    echo "2. Run: ${YELLOW}./scripts/start.sh${NC} to start all services"
    echo "3. Visit: ${BLUE}http://localhost:12000${NC} to access the web interface"
    echo ""
    echo -e "${CYAN}Useful commands:${NC}"
    echo "• Start services: ${YELLOW}./scripts/start.sh${NC}"
    echo "• Stop services: ${YELLOW}./scripts/stop.sh${NC}"
    echo "• View logs: ${YELLOW}./scripts/logs.sh${NC}"
    echo "• Backup data: ${YELLOW}./scripts/backup.sh${NC}"
    echo ""
    echo -e "${PURPLE}The Scribe awaits your command! ✨${NC}"
}

# Run main function
main "$@"