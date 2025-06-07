# 🔧 Aetherium Troubleshooting Guide

This guide covers common issues and their solutions when running the Aetherium system.

## 🚀 Quick Fixes

### 1. Complete System Reset
If you're experiencing multiple issues, try a complete reset:

```bash
# Stop all services and remove volumes
docker compose down --volumes --remove-orphans

# Remove all Docker images (optional, for complete fresh start)
docker system prune -a

# Start fresh
./start-aetherium.sh
```

### 2. Check System Status
```bash
# Check all services
docker compose ps

# Check specific service logs
docker compose logs backend-api
docker compose logs database
docker compose logs web-frontend
```

## 🐛 Common Issues

### Database Issues

**Problem**: `password authentication failed for user "demo_user"`
```bash
# Solution: Reset database with correct credentials
docker compose down
docker volume rm ozodbek-_postgres_data
./start-aetherium.sh
```

**Problem**: `database "aetherium_demo" does not exist`
```bash
# Solution: Check environment variables and restart
cat .env | grep POSTGRES
docker compose down
docker volume rm ozodbek-_postgres_data
docker compose up -d database
sleep 10
docker compose up -d backend-api
```

### Backend API Issues

**Problem**: `ModuleNotFoundError: No module named 'utils.exceptions'`
```bash
# Solution: Rebuild backend image
docker compose build backend-api --no-cache
docker compose up -d backend-api
```

**Problem**: `object async_generator can't be used in 'await' expression`
```bash
# Solution: This is a known issue with health checks, backend still works
# Check if API is responding:
curl http://localhost:8000/docs
```

**Problem**: `ImportError: cannot import name 'jwt' from 'jose'`
```bash
# Solution: Rebuild with updated dependencies
docker compose build backend-api --no-cache
docker compose up -d backend-api
```

### Frontend Issues

**Problem**: `Module not found: Can't resolve './components/LanguageSelector'`
```bash
# Solution: Rebuild frontend
docker compose build web-frontend --no-cache
docker compose up -d web-frontend
```

**Problem**: Frontend not accessible on port 12000
```bash
# Check if port is in use
sudo lsof -i :12000

# Restart frontend
docker compose restart web-frontend

# Check logs
docker compose logs web-frontend
```

### Docker Issues

**Problem**: `port is already allocated`
```bash
# Find what's using the port
sudo lsof -i :8000
sudo lsof -i :12000
sudo lsof -i :5432

# Stop conflicting services
docker compose down
# Kill specific process if needed
sudo kill -9 <PID>
```

**Problem**: `no space left on device`
```bash
# Clean up Docker
docker system prune -a
docker volume prune

# Remove unused images
docker image prune -a
```

## 🔍 Diagnostic Commands

### System Health Check
```bash
# Check all services
./start-aetherium.sh --logs

# Manual health checks
curl http://localhost:8000/health
curl http://localhost:12000
docker compose exec database pg_isready -U demo_user -d aetherium_demo
docker compose exec redis redis-cli ping
```

### Log Analysis
```bash
# View all logs
docker compose logs

# View specific service logs with timestamps
docker compose logs -t backend-api

# Follow logs in real-time
docker compose logs -f backend-api

# View last 50 lines
docker compose logs --tail=50 backend-api
```

### Resource Usage
```bash
# Check Docker resource usage
docker stats

# Check disk usage
docker system df

# Check container details
docker compose ps -a
```

## 🛠️ Advanced Troubleshooting

### Database Connection Testing
```bash
# Connect to database directly
docker compose exec database psql -U demo_user -d aetherium_demo

# Check database tables
docker compose exec database psql -U demo_user -d aetherium_demo -c "\dt"

# Check database connections
docker compose exec database psql -U demo_user -d aetherium_demo -c "SELECT * FROM pg_stat_activity;"
```

### Backend API Testing
```bash
# Test API endpoints
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/docs
curl -X GET http://localhost:8000/api/v1/users/me

# Check backend environment
docker compose exec backend-api env | grep -E "(DATABASE|JWT|REDIS)"
```

### Frontend Debugging
```bash
# Check frontend build
docker compose exec web-frontend npm run build

# Check frontend dependencies
docker compose exec web-frontend npm list

# Access frontend container
docker compose exec web-frontend sh
```

## 🔧 Configuration Issues

### Environment Variables
```bash
# Check .env file
cat .env

# Verify environment variables are loaded
docker compose config

# Check specific service environment
docker compose exec backend-api printenv | grep DATABASE_URL
```

### Docker Compose Issues
```bash
# Validate docker compose.yml
docker compose config

# Check service dependencies
docker compose config --services

# Rebuild specific service
docker compose build backend-api --no-cache
```

## 🚨 Emergency Procedures

### Complete System Recovery
```bash
#!/bin/bash
# Emergency recovery script

echo "🚨 Starting emergency recovery..."

# Stop everything
docker compose down --volumes --remove-orphans

# Clean Docker system
docker system prune -f
docker volume prune -f

# Remove project volumes
docker volume rm ozodbek-_postgres_data 2>/dev/null || true
docker volume rm ozodbek-_redis_data 2>/dev/null || true

# Rebuild everything
docker compose build --no-cache

# Start with fresh data
./start-aetherium.sh

echo "✅ Emergency recovery completed"
```

### Backup and Restore
```bash
# Backup database
docker compose exec database pg_dump -U demo_user aetherium_demo > backup.sql

# Restore database
docker compose exec -T database psql -U demo_user aetherium_demo < backup.sql
```

## 📞 Getting Help

### Log Collection for Support
```bash
# Collect all logs
mkdir -p logs
docker compose logs > logs/all-services.log
docker compose logs backend-api > logs/backend.log
docker compose logs database > logs/database.log
docker compose logs web-frontend > logs/frontend.log

# System information
docker version > logs/docker-version.txt
docker compose version > logs/compose-version.txt
uname -a > logs/system-info.txt
```

### Performance Monitoring
```bash
# Monitor resource usage
docker stats --no-stream > logs/resource-usage.txt

# Check service health
curl -s http://localhost:8000/health > logs/backend-health.txt
curl -s -I http://localhost:12000 > logs/frontend-health.txt
```

## 🔍 Known Issues

### 1. Health Check Failures
- **Issue**: Backend health check shows "unhealthy" but API works
- **Cause**: Async generator issue in health endpoint
- **Workaround**: Check API docs at http://localhost:8000/docs instead

### 2. Slow Startup
- **Issue**: Services take long to start
- **Cause**: Database initialization and image building
- **Solution**: Use `./start-aetherium.sh` which handles timing

### 3. Port Conflicts
- **Issue**: Ports 8000, 12000, 5432 already in use
- **Solution**: Stop conflicting services or change ports in docker compose.yml

### 4. Memory Issues
- **Issue**: Out of memory errors
- **Solution**: Increase Docker memory allocation to 4GB+

## 📋 Maintenance

### Regular Maintenance
```bash
# Weekly cleanup
docker system prune
docker volume prune

# Update images
docker compose pull
docker compose build --no-cache

# Restart services
./start-aetherium.sh
```

### Performance Optimization
```bash
# Database maintenance
docker compose exec database psql -U demo_user -d aetherium_demo -c "VACUUM ANALYZE;"

# Clear Redis cache
docker compose exec redis redis-cli FLUSHALL

# Restart services for fresh memory
docker compose restart
```

---

**Need more help?** 
- Check the [main README](README.md) for setup instructions
- Open an issue on GitHub with logs and system information
- Contact support with the collected logs from the "Getting Help" section