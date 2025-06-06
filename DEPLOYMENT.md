# Aetherium Deployment Guide

## Quick Start

The entire Aetherium platform can be deployed with a single command:

```bash
./start.sh
```

This script will:
1. Check prerequisites
2. Build all Docker images
3. Start all services
4. Verify system health
5. Display access information

## Prerequisites

### Hardware Requirements

- **Server**: 64GB RAM, NVIDIA Tesla V100 GPU
- **PCI Slots**: 15 PCI 1x slots for USB expansion
- **GSM Modems**: Up to 40 SIM800C modems with dual USB connections
- **Storage**: 2TB NVMe SSD (enterprise grade)

### Software Requirements

- **OS**: Ubuntu Server 20.04 LTS or newer
- **Docker**: Version 20.10 or newer
- **Docker Compose**: Version 2.0 or newer
- **Git**: For repository management

## Environment Configuration

1. **Copy Environment Template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure Required Variables**:
   ```bash
   # Database
   POSTGRES_PASSWORD=your_secure_password
   
   # Security
   JWT_SECRET_KEY=your_32_character_jwt_secret_key
   ENCRYPTION_KEY=your_32_character_encryption_key
   
   # External APIs
   GEMINI_API_KEY=your_gemini_api_key
   CLICK_MERCHANT_ID=your_click_merchant_id
   CLICK_SECRET_KEY=your_click_secret_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   SMS_API_KEY=your_sms_api_key
   ```

## Manual Deployment

If you prefer manual control:

1. **Build Images**:
   ```bash
   docker-compose build
   ```

2. **Start Services**:
   ```bash
   docker-compose up -d
   ```

3. **Check Status**:
   ```bash
   docker-compose ps
   ```

## Service Architecture

The platform consists of 6 main services:

- **Database** (PostgreSQL): Data storage
- **Backend API** (FastAPI): Core business logic
- **Frontend** (React): Web interface
- **Modem Manager** (Python): GSM hardware control
- **Telegram Bot** (Python): Telegram integration
- **Nginx** (Optional): Reverse proxy

## Hardware Setup

### GSM Modem Configuration

1. **Physical Installation**:
   - Install PCI USB expansion cards in all 15 slots
   - Connect each SIM800C modem with two USB cables
   - One cable for AT commands (`/dev/ttyUSB*`)
   - One cable for audio (`/dev/snd/*`)

2. **Device Permissions**:
   ```bash
   # Add user to dialout group
   sudo usermod -a -G dialout $USER
   
   # Set udev rules for consistent device naming
   sudo cp docker/99-aetherium-modems.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   ```

3. **Audio System**:
   ```bash
   # Install ALSA utilities
   sudo apt-get install alsa-utils
   
   # Check audio devices
   aplay -l
   arecord -l
   ```

## Network Configuration

### Port Mapping

- **80/443**: Nginx (if used)
- **8000**: Backend API
- **8001**: Modem Manager
- **12000**: Frontend (development)
- **5432**: PostgreSQL (internal)

### Firewall Setup

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow API access (if needed externally)
sudo ufw allow 8000

# Allow SSH
sudo ufw allow 22

# Enable firewall
sudo ufw enable
```

## SSL/TLS Configuration

For production deployment with SSL:

1. **Obtain SSL Certificate**:
   ```bash
   # Using Let's Encrypt
   sudo apt-get install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

2. **Configure Nginx**:
   ```bash
   # Copy SSL certificates
   sudo cp /etc/letsencrypt/live/your-domain.com/* docker/ssl/
   
   # Update nginx configuration
   # Edit docker/nginx.conf for SSL settings
   ```

## Monitoring and Maintenance

### Log Management

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs -f backend-api

# View last 100 lines
docker-compose logs --tail=100 modem-manager
```

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Check database connection
docker exec -it aetherium_database psql -U aetherium_user -d aetherium -c "SELECT 1;"
```

### Backup Procedures

```bash
# Database backup
docker exec aetherium_database pg_dump -U aetherium_user aetherium > backup_$(date +%Y%m%d).sql

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

### Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d

# Clean old images
docker image prune -f
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   ```bash
   # Check database logs
   docker-compose logs database
   
   # Restart database
   docker-compose restart database
   ```

2. **Modem Not Detected**:
   ```bash
   # Check USB devices
   lsusb
   
   # Check serial ports
   ls -la /dev/ttyUSB*
   
   # Restart modem manager
   docker-compose restart modem-manager
   ```

3. **Audio Issues**:
   ```bash
   # Check ALSA devices
   aplay -l
   
   # Test audio capture
   arecord -f cd -t wav -d 5 test.wav
   ```

4. **High Memory Usage**:
   ```bash
   # Check container memory usage
   docker stats
   
   # Restart services if needed
   docker-compose restart
   ```

### Performance Optimization

1. **Database Tuning**:
   ```sql
   -- Optimize PostgreSQL settings
   ALTER SYSTEM SET shared_buffers = '16GB';
   ALTER SYSTEM SET effective_cache_size = '48GB';
   ALTER SYSTEM SET maintenance_work_mem = '2GB';
   SELECT pg_reload_conf();
   ```

2. **System Limits**:
   ```bash
   # Increase file descriptor limits
   echo "* soft nofile 65536" >> /etc/security/limits.conf
   echo "* hard nofile 65536" >> /etc/security/limits.conf
   ```

## Security Considerations

### API Security

- All API endpoints use JWT authentication
- Sensitive data is encrypted at rest
- Rate limiting is implemented
- CORS is properly configured

### Network Security

- Use HTTPS in production
- Implement proper firewall rules
- Regular security updates
- Monitor access logs

### Data Protection

- Bank card numbers are encrypted
- User passwords are hashed
- Session data is secured
- Regular backups are encrypted

## Production Checklist

- [ ] SSL certificates configured
- [ ] Environment variables secured
- [ ] Database backups automated
- [ ] Monitoring system deployed
- [ ] Log rotation configured
- [ ] Firewall rules applied
- [ ] Hardware properly installed
- [ ] Performance testing completed
- [ ] Security audit performed
- [ ] Documentation updated

## Support

For technical support:
1. Check logs for error messages
2. Verify hardware connections
3. Test network connectivity
4. Review configuration files
5. Consult troubleshooting guide

The Scribe awaits your command. May your deployment be swift and your conversations flow like ink upon parchment.