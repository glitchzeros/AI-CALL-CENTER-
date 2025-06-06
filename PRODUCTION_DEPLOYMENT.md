# Aetherium Production Deployment Guide
## The Scribe's Awakening in the Real World

This guide provides step-by-step instructions for deploying the Aetherium AI Call Center Platform in a production environment.

## 🏗️ Hardware Requirements

### Server Specifications (Absolute Requirements)
- **CPU**: Intel Xeon Gold 6xxx or AMD EPYC 7xxx (minimum 40 cores/threads)
- **RAM**: 64GB DDR4/DDR5 ECC Registered
- **GPU**: NVIDIA Tesla V100 (16GB or 32GB VRAM)
- **Storage**: 2TB+ NVMe SSD (enterprise-grade)
- **PCI Slots**: Minimum 15 PCI Express 1x slots
- **Network**: 1GbE or 10GbE Ethernet
- **Power**: Sufficient PSU for all components + cooling

### GSM Modem Setup
- **Modems**: SIM800C GSM modems (up to 40 units)
- **USB Expansion**: PCI-based USB hub cards for 15 PCI slots
- **Connections**: Each modem requires 2 USB ports (control + audio)
- **SIM Cards**: Active SIM cards for each modem
- **Antennas**: GSM antennas for signal reception

## 🔧 Software Prerequisites

### Operating System
```bash
# Ubuntu Server 22.04 LTS (recommended)
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt install -y git curl wget htop iotop usbutils
```

### GPU Drivers
```bash
# Install NVIDIA drivers and CUDA
sudo apt install -y nvidia-driver-535 nvidia-cuda-toolkit
sudo reboot

# Verify GPU
nvidia-smi
```

### USB Device Management
```bash
# Install USB utilities
sudo apt install -y usbutils usb-modeswitch

# Create udev rules for modem stability
sudo nano /etc/udev/rules.d/99-gsm-modems.rules
```

Add to udev rules:
```
# GSM Modem Rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="1e0e", ATTRS{idProduct}=="9001", SYMLINK+="gsm_modem_%n"
SUBSYSTEM=="sound", ATTRS{idVendor}=="1e0e", ATTRS{idProduct}=="9001", SYMLINK+="gsm_audio_%n"
```

## 🚀 Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/BarnoxonBuvijon/Ai-call-center-agent-.git
cd Ai-call-center-agent-
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables:**
```bash
# Database
DB_PASSWORD=your_secure_database_password

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_from_google_ai_studio

# Company Bank Details (for manual payments)
COMPANY_BANK_CARD=8600123456789012
COMPANY_BANK_NAME=Your_Bank_Name
COMPANY_CARDHOLDER_NAME=Your_Company_Name
COMPANY_BANK_PHONE=+998901234567

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Security
JWT_SECRET_KEY=your_very_secure_jwt_secret_minimum_32_chars
ENCRYPTION_KEY=your_32_character_encryption_key
```

### 3. SSL Certificate Setup (Production)
```bash
# Create SSL directory
mkdir -p docker/ssl

# Option A: Let's Encrypt (recommended)
sudo apt install -y certbot
sudo certbot certonly --standalone -d your-domain.com
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/ssl/key.pem

# Option B: Self-signed (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/key.pem \
  -out docker/ssl/cert.pem
```

### 4. Hardware Verification
```bash
# Check GPU
nvidia-smi

# Check USB devices
lsusb

# Check PCI slots
lspci | grep -i usb

# Verify modem detection
ls /dev/ttyUSB*
ls /dev/snd/pcm*
```

### 5. Deploy Platform
```bash
# Make start script executable
chmod +x start.sh

# Deploy the entire platform
./start.sh
```

The script will:
- Verify prerequisites
- Build Docker images
- Start all services
- Perform health checks
- Display access information

### 6. Post-Deployment Verification

#### Check Service Status
```bash
docker-compose ps
docker-compose logs -f
```

#### Test API Endpoints
```bash
# Backend health
curl http://localhost:8000/health

# Frontend access
curl http://localhost:12000

# Modem manager
curl http://localhost:8001/health
```

#### Verify Database
```bash
docker-compose exec database psql -U aetherium_user -d aetherium -c "\dt"
```

## 🔒 Security Configuration

### Firewall Setup
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # Backend API (internal)
sudo ufw allow 8001/tcp  # Modem Manager (internal)
```

### SSL/TLS Configuration
- Use strong cipher suites (configured in nginx.conf)
- Enable HTTP/2
- Set security headers
- Configure HSTS

### Database Security
- Use strong passwords
- Enable SSL connections
- Regular backups
- Access logging

## 📊 Monitoring & Maintenance

### Log Management
```bash
# View service logs
docker-compose logs -f [service_name]

# Log rotation
sudo nano /etc/logrotate.d/aetherium
```

### Health Monitoring
```bash
# System resources
htop
iotop
nvidia-smi

# Service health
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Backup Strategy
```bash
# Database backup
docker-compose exec database pg_dump -U aetherium_user aetherium > backup_$(date +%Y%m%d).sql

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker/ database/
```

## 🔄 Updates & Maintenance

### Platform Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

### Database Migrations
```bash
# Backup before migration
docker-compose exec database pg_dump -U aetherium_user aetherium > pre_migration_backup.sql

# Apply migrations (if any)
docker-compose exec backend-api python -m alembic upgrade head
```

## 🚨 Troubleshooting

### Common Issues

#### Modem Detection Problems
```bash
# Check USB devices
lsusb
dmesg | grep -i usb

# Restart modem manager
docker-compose restart modem-manager
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs database

# Verify connection
docker-compose exec database psql -U aetherium_user -d aetherium -c "SELECT 1;"
```

#### GPU Not Detected
```bash
# Check NVIDIA drivers
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Performance Optimization

#### Database Tuning
```sql
-- Optimize PostgreSQL for high concurrency
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '16GB';
ALTER SYSTEM SET effective_cache_size = '48GB';
ALTER SYSTEM SET work_mem = '256MB';
```

#### System Tuning
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize network settings
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" >> /etc/sysctl.conf
```

## 📞 Support & Contact

For technical support and deployment assistance:
- GitHub Issues: https://github.com/BarnoxonBuvijon/Ai-call-center-agent-/issues
- Documentation: Check README.md and other .md files in the repository

## 🎯 Success Metrics

A successful deployment should achieve:
- ✅ All Docker services running and healthy
- ✅ Database accessible and populated with schema
- ✅ Frontend accessible via web browser
- ✅ API endpoints responding correctly
- ✅ GSM modems detected and initialized
- ✅ GPU available for AI processing
- ✅ WebSocket connections working
- ✅ SSL certificates valid (production)

**The Scribe Awaits Your Command** 🎭

*"Where AI Scribes dwell and conversations flow like ink upon parchment"*