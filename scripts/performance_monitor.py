#!/usr/bin/env python3
"""
Aetherium Performance Monitoring Script
Monitor system resources and performance metrics
"""

import asyncio
import aiohttp
import json
import time
import subprocess
import psutil
from datetime import datetime
from typing import Dict, List

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        
    def get_system_metrics(self) -> Dict:
        """Get system resource metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_recv': psutil.net_io_counters().packets_recv
            }
        }
    
    def get_docker_metrics(self) -> List[Dict]:
        """Get Docker container metrics"""
        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", 
                 "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                containers = []
                
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 6:
                            containers.append({
                                'container': parts[0],
                                'cpu_percent': parts[1],
                                'memory_usage': parts[2],
                                'memory_percent': parts[3],
                                'network_io': parts[4],
                                'block_io': parts[5]
                            })
                
                return containers
            else:
                return []
        except Exception as e:
            print(f"Error getting Docker metrics: {e}")
            return []
    
    async def get_service_response_times(self) -> Dict:
        """Measure service response times"""
        services = {
            'backend_health': 'http://localhost:8000/health',
            'frontend_12000': 'http://localhost:12000/',
            'frontend_12001': 'http://localhost:12001/'
        }
        
        response_times = {}
        
        for service, url in services.items():
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        end_time = time.time()
                        response_times[service] = {
                            'response_time_ms': round((end_time - start_time) * 1000, 2),
                            'status_code': response.status,
                            'success': response.status < 400
                        }
            except Exception as e:
                response_times[service] = {
                    'response_time_ms': None,
                    'status_code': None,
                    'success': False,
                    'error': str(e)
                }
        
        return response_times
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    async def run_monitoring_cycle(self, duration_minutes: int = 5):
        """Run monitoring for specified duration"""
        print(f"🔍 Starting Aetherium Performance Monitoring")
        print(f"⏱️ Duration: {duration_minutes} minutes")
        print("=" * 60)
        
        cycles = duration_minutes * 2  # Every 30 seconds
        
        for cycle in range(cycles):
            print(f"\n📊 Monitoring Cycle {cycle + 1}/{cycles}")
            print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # System metrics
            system_metrics = self.get_system_metrics()
            print(f"\n💻 System Resources:")
            print(f"  CPU Usage: {system_metrics['cpu_percent']:.1f}%")
            print(f"  Memory: {system_metrics['memory']['percent']:.1f}% "
                  f"({self.format_bytes(system_metrics['memory']['used'])}/"
                  f"{self.format_bytes(system_metrics['memory']['total'])})")
            print(f"  Disk: {system_metrics['disk']['percent']:.1f}% "
                  f"({self.format_bytes(system_metrics['disk']['used'])}/"
                  f"{self.format_bytes(system_metrics['disk']['total'])})")
            
            # Docker metrics
            docker_metrics = self.get_docker_metrics()
            if docker_metrics:
                print(f"\n🐳 Docker Containers:")
                for container in docker_metrics:
                    print(f"  {container['container']}: "
                          f"CPU {container['cpu_percent']}, "
                          f"Memory {container['memory_usage']} ({container['memory_percent']})")
            
            # Service response times
            response_times = await self.get_service_response_times()
            print(f"\n⚡ Service Response Times:")
            for service, metrics in response_times.items():
                if metrics['success']:
                    print(f"  {service}: {metrics['response_time_ms']}ms (Status: {metrics['status_code']})")
                else:
                    error_msg = metrics.get('error', 'Unknown error')
                    print(f"  {service}: ❌ Failed ({error_msg})")
            
            # Performance warnings
            warnings = []
            if system_metrics['cpu_percent'] > 80:
                warnings.append(f"⚠️ High CPU usage: {system_metrics['cpu_percent']:.1f}%")
            if system_metrics['memory']['percent'] > 85:
                warnings.append(f"⚠️ High memory usage: {system_metrics['memory']['percent']:.1f}%")
            if system_metrics['disk']['percent'] > 90:
                warnings.append(f"⚠️ High disk usage: {system_metrics['disk']['percent']:.1f}%")
            
            for service, metrics in response_times.items():
                if metrics['success'] and metrics['response_time_ms'] and metrics['response_time_ms'] > 5000:
                    warnings.append(f"⚠️ Slow response from {service}: {metrics['response_time_ms']}ms")
            
            if warnings:
                print(f"\n⚠️ Performance Warnings:")
                for warning in warnings:
                    print(f"  {warning}")
            else:
                print(f"\n✅ All systems performing within normal parameters")
            
            if cycle < cycles - 1:  # Don't sleep on last cycle
                print(f"\n⏳ Waiting 30 seconds for next cycle...")
                await asyncio.sleep(30)
        
        print(f"\n🏁 Monitoring completed!")
    
    async def quick_check(self):
        """Run a quick performance check"""
        print("⚡ Quick Performance Check")
        print("=" * 30)
        
        # System metrics
        system_metrics = self.get_system_metrics()
        print(f"\n💻 System Status:")
        print(f"  CPU: {system_metrics['cpu_percent']:.1f}%")
        print(f"  Memory: {system_metrics['memory']['percent']:.1f}%")
        print(f"  Disk: {system_metrics['disk']['percent']:.1f}%")
        
        # Service response times
        response_times = await self.get_service_response_times()
        print(f"\n⚡ Service Response Times:")
        for service, metrics in response_times.items():
            if metrics['success']:
                status = "🟢" if metrics['response_time_ms'] < 1000 else "🟡" if metrics['response_time_ms'] < 3000 else "🔴"
                print(f"  {status} {service}: {metrics['response_time_ms']}ms")
            else:
                print(f"  🔴 {service}: Failed")

async def main():
    import sys
    
    monitor = PerformanceMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            await monitor.quick_check()
        elif sys.argv[1].isdigit():
            duration = int(sys.argv[1])
            await monitor.run_monitoring_cycle(duration)
        else:
            print("Usage: python performance_monitor.py [quick|duration_minutes]")
            sys.exit(1)
    else:
        await monitor.quick_check()

if __name__ == "__main__":
    asyncio.run(main())