#!/usr/bin/env python3
"""
Aetherium System Health Check Script
Comprehensive health monitoring for all system components
"""

import asyncio
import aiohttp
import json
import sys
import time
from typing import Dict, List, Tuple
import subprocess
import os

class HealthChecker:
    def __init__(self):
        self.results = {}
        self.base_url = "http://localhost"
        
    async def check_service_health(self, service_name: str, port: int, endpoint: str = "/health", expect_json: bool = True) -> Tuple[bool, str]:
        """Check if a service is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}:{port}{endpoint}", timeout=10) as response:
                    if response.status == 200:
                        if expect_json:
                            data = await response.json()
                        return True, f"✅ {service_name} is healthy"
                    else:
                        return False, f"❌ {service_name} returned status {response.status}"
        except asyncio.TimeoutError:
            return False, f"⏰ {service_name} timed out"
        except Exception as e:
            return False, f"❌ {service_name} error: {str(e)}"
    
    def check_docker_containers(self) -> List[Tuple[bool, str]]:
        """Check Docker container status"""
        results = []
        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                cwd="/workspace/Ozodbek-"
            )
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            container = json.loads(line)
                            containers.append(container)
                        except json.JSONDecodeError:
                            continue
                
                for container in containers:
                    name = container.get('Name', 'Unknown')
                    state = container.get('State', 'Unknown')
                    health = container.get('Health', 'Unknown')
                    
                    if state == 'running':
                        if health in ['healthy', 'Unknown']:
                            results.append((True, f"✅ {name}: {state} ({health})"))
                        else:
                            results.append((False, f"⚠️ {name}: {state} but {health}"))
                    else:
                        results.append((False, f"❌ {name}: {state}"))
            else:
                results.append((False, f"❌ Docker Compose error: {result.stderr}"))
                
        except Exception as e:
            results.append((False, f"❌ Docker check failed: {str(e)}"))
        
        return results
    
    def check_ports(self) -> List[Tuple[bool, str]]:
        """Check if required ports are accessible"""
        ports = {
            8000: "Backend API",
            12000: "Frontend (primary)",
            12001: "Frontend (fallback)",
            5432: "PostgreSQL",
            6379: "Redis"
        }
        
        results = []
        for port, service in ports.items():
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    results.append((True, f"✅ Port {port} ({service}) is open"))
                else:
                    results.append((False, f"❌ Port {port} ({service}) is closed"))
            except Exception as e:
                results.append((False, f"❌ Port {port} check failed: {str(e)}"))
        
        return results
    
    def check_environment_files(self) -> List[Tuple[bool, str]]:
        """Check environment configuration"""
        results = []
        
        # Check .env file
        env_path = "/workspace/Ozodbek-/.env"
        if os.path.exists(env_path):
            results.append((True, "✅ .env file exists"))
            
            # Check critical environment variables
            with open(env_path, 'r') as f:
                env_content = f.read()
                
            critical_vars = [
                'POSTGRES_PASSWORD',
                'JWT_SECRET_KEY',
                'DATABASE_URL'
            ]
            
            for var in critical_vars:
                if var in env_content and not env_content.split(f'{var}=')[1].split('\n')[0].strip() == '':
                    results.append((True, f"✅ {var} is configured"))
                else:
                    results.append((False, f"❌ {var} is missing or empty"))
        else:
            results.append((False, "❌ .env file is missing"))
        
        return results
    
    async def run_comprehensive_check(self):
        """Run all health checks"""
        print("🔍 Aetherium System Health Check")
        print("=" * 50)
        
        # Docker containers check
        print("\n📦 Docker Containers:")
        docker_results = self.check_docker_containers()
        for success, message in docker_results:
            print(f"  {message}")
        
        # Port accessibility check
        print("\n🔌 Port Accessibility:")
        port_results = self.check_ports()
        for success, message in port_results:
            print(f"  {message}")
        
        # Environment configuration check
        print("\n⚙️ Environment Configuration:")
        env_results = self.check_environment_files()
        for success, message in env_results:
            print(f"  {message}")
        
        # Service health checks
        print("\n🏥 Service Health Endpoints:")
        
        # Backend API
        backend_health = await self.check_service_health("Backend API", 8000)
        print(f"  {backend_health[1]}")
        
        # Frontend (try both ports)
        frontend_12000 = await self.check_service_health("Frontend (12000)", 12000, "/", expect_json=False)
        frontend_12001 = await self.check_service_health("Frontend (12001)", 12001, "/", expect_json=False)
        print(f"  {frontend_12000[1]}")
        print(f"  {frontend_12001[1]}")
        
        # Calculate overall health
        all_results = docker_results + port_results + env_results + [backend_health, frontend_12000, frontend_12001]
        total_checks = len(all_results)
        successful_checks = sum(1 for success, _ in all_results if success)
        
        print(f"\n📊 Overall System Health:")
        print(f"  Successful checks: {successful_checks}/{total_checks}")
        print(f"  Health percentage: {(successful_checks/total_checks)*100:.1f}%")
        
        if successful_checks == total_checks:
            print("  🎉 System is fully operational!")
            return 0
        elif successful_checks >= total_checks * 0.8:
            print("  ⚠️ System is mostly operational with minor issues")
            return 1
        else:
            print("  ❌ System has significant issues requiring attention")
            return 2

async def main():
    checker = HealthChecker()
    exit_code = await checker.run_comprehensive_check()
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())