#!/usr/bin/env python3
"""
Aetherium Backup and Restore Script
Comprehensive backup and restore functionality for the entire system
"""

import os
import sys
import subprocess
import json
import tarfile
import shutil
from datetime import datetime
from pathlib import Path
import argparse

class BackupRestore:
    def __init__(self):
        self.project_root = Path("/workspace/Ozodbek-")
        self.backup_dir = self.project_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_database_backup(self, backup_path: Path) -> bool:
        """Create PostgreSQL database backup"""
        try:
            print("📦 Creating database backup...")
            
            # Get database connection info from environment
            env_file = self.project_root / ".env"
            db_config = {}
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            db_config[key] = value
            
            db_name = db_config.get('POSTGRES_DB', 'aetherium')
            db_user = db_config.get('POSTGRES_USER', 'aetherium_user')
            db_password = db_config.get('POSTGRES_PASSWORD', '')
            
            # Create database dump
            dump_file = backup_path / "database_dump.sql"
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            
            result = subprocess.run([
                'docker', 'exec', 'aetherium_database',
                'pg_dump', '-U', db_user, '-d', db_name
            ], stdout=open(dump_file, 'w'), stderr=subprocess.PIPE, env=env)
            
            if result.returncode == 0:
                print(f"✅ Database backup created: {dump_file}")
                return True
            else:
                print(f"❌ Database backup failed: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Database backup error: {e}")
            return False
    
    def create_files_backup(self, backup_path: Path) -> bool:
        """Create backup of important files"""
        try:
            print("📁 Creating files backup...")
            
            # Important directories and files to backup
            important_paths = [
                'backend/uploads',
                'backend/logs',
                'modem-manager/logs',
                '.env',
                '.env.example',
                'docker-compose.yml',
                'docker-compose.dev.yml',
                'docker-compose.prod.yml'
            ]
            
            files_backup = backup_path / "files_backup.tar.gz"
            
            with tarfile.open(files_backup, 'w:gz') as tar:
                for path_str in important_paths:
                    path = self.project_root / path_str
                    if path.exists():
                        tar.add(path, arcname=path_str)
                        print(f"  📄 Added: {path_str}")
            
            print(f"✅ Files backup created: {files_backup}")
            return True
            
        except Exception as e:
            print(f"❌ Files backup error: {e}")
            return False
    
    def create_docker_images_backup(self, backup_path: Path) -> bool:
        """Create backup of Docker images"""
        try:
            print("🐳 Creating Docker images backup...")
            
            # Get list of project images
            result = subprocess.run([
                'docker', 'images', '--format', 'json'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to list Docker images: {result.stderr}")
                return False
            
            project_images = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        image_info = json.loads(line)
                        repo = image_info.get('Repository', '')
                        if 'ozodbek-' in repo or 'aetherium' in repo:
                            project_images.append(f"{repo}:{image_info.get('Tag', 'latest')}")
                    except json.JSONDecodeError:
                        continue
            
            if not project_images:
                print("⚠️ No project-specific Docker images found")
                return True
            
            # Save each image
            images_dir = backup_path / "docker_images"
            images_dir.mkdir(exist_ok=True)
            
            for image in project_images:
                safe_name = image.replace(':', '_').replace('/', '_')
                image_file = images_dir / f"{safe_name}.tar"
                
                print(f"  🐳 Saving image: {image}")
                result = subprocess.run([
                    'docker', 'save', '-o', str(image_file), image
                ], capture_output=True)
                
                if result.returncode == 0:
                    print(f"    ✅ Saved: {image_file}")
                else:
                    print(f"    ❌ Failed to save {image}: {result.stderr.decode()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Docker images backup error: {e}")
            return False
    
    def create_backup(self, backup_name: str = None) -> bool:
        """Create complete system backup"""
        if not backup_name:
            backup_name = f"aetherium_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        print(f"🚀 Creating backup: {backup_name}")
        print(f"📍 Backup location: {backup_path}")
        print("=" * 50)
        
        # Create backup metadata
        metadata = {
            'backup_name': backup_name,
            'created_at': datetime.now().isoformat(),
            'version': '1.0',
            'components': []
        }
        
        success = True
        
        # Database backup
        if self.create_database_backup(backup_path):
            metadata['components'].append('database')
        else:
            success = False
        
        # Files backup
        if self.create_files_backup(backup_path):
            metadata['components'].append('files')
        else:
            success = False
        
        # Docker images backup
        if self.create_docker_images_backup(backup_path):
            metadata['components'].append('docker_images')
        else:
            success = False
        
        # Save metadata
        with open(backup_path / "backup_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        if success:
            print(f"\n🎉 Backup completed successfully!")
            print(f"📦 Backup size: {self.get_directory_size(backup_path)}")
        else:
            print(f"\n⚠️ Backup completed with some errors")
        
        return success
    
    def restore_database(self, backup_path: Path) -> bool:
        """Restore database from backup"""
        try:
            print("🔄 Restoring database...")
            
            dump_file = backup_path / "database_dump.sql"
            if not dump_file.exists():
                print("❌ Database dump file not found")
                return False
            
            # Get database connection info
            env_file = self.project_root / ".env"
            db_config = {}
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            db_config[key] = value
            
            db_name = db_config.get('POSTGRES_DB', 'aetherium')
            db_user = db_config.get('POSTGRES_USER', 'aetherium_user')
            db_password = db_config.get('POSTGRES_PASSWORD', '')
            
            # Restore database
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            
            with open(dump_file, 'r') as f:
                result = subprocess.run([
                    'docker', 'exec', '-i', 'aetherium_database',
                    'psql', '-U', db_user, '-d', db_name
                ], stdin=f, stderr=subprocess.PIPE, env=env)
            
            if result.returncode == 0:
                print("✅ Database restored successfully")
                return True
            else:
                print(f"❌ Database restore failed: {result.stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Database restore error: {e}")
            return False
    
    def restore_files(self, backup_path: Path) -> bool:
        """Restore files from backup"""
        try:
            print("📁 Restoring files...")
            
            files_backup = backup_path / "files_backup.tar.gz"
            if not files_backup.exists():
                print("❌ Files backup not found")
                return False
            
            # Extract files
            with tarfile.open(files_backup, 'r:gz') as tar:
                tar.extractall(path=self.project_root)
            
            print("✅ Files restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Files restore error: {e}")
            return False
    
    def restore_docker_images(self, backup_path: Path) -> bool:
        """Restore Docker images from backup"""
        try:
            print("🐳 Restoring Docker images...")
            
            images_dir = backup_path / "docker_images"
            if not images_dir.exists():
                print("⚠️ Docker images backup not found")
                return True
            
            # Load each image
            for image_file in images_dir.glob("*.tar"):
                print(f"  🐳 Loading image: {image_file.name}")
                result = subprocess.run([
                    'docker', 'load', '-i', str(image_file)
                ], capture_output=True)
                
                if result.returncode == 0:
                    print(f"    ✅ Loaded: {image_file.name}")
                else:
                    print(f"    ❌ Failed to load {image_file.name}: {result.stderr.decode()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Docker images restore error: {e}")
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore complete system from backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        # Load metadata
        metadata_file = backup_path / "backup_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            print(f"📋 Backup info: {metadata.get('created_at', 'Unknown date')}")
        else:
            print("⚠️ Backup metadata not found, proceeding anyway...")
        
        print(f"🔄 Restoring backup: {backup_name}")
        print("=" * 50)
        
        success = True
        
        # Restore components
        if self.restore_files(backup_path):
            pass
        else:
            success = False
        
        if self.restore_docker_images(backup_path):
            pass
        else:
            success = False
        
        if self.restore_database(backup_path):
            pass
        else:
            success = False
        
        if success:
            print(f"\n🎉 Restore completed successfully!")
        else:
            print(f"\n⚠️ Restore completed with some errors")
        
        return success
    
    def list_backups(self):
        """List available backups"""
        print("📋 Available Backups:")
        print("=" * 30)
        
        backups = []
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                metadata_file = backup_dir / "backup_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    backups.append((backup_dir.name, metadata))
                else:
                    backups.append((backup_dir.name, {'created_at': 'Unknown'}))
        
        if not backups:
            print("No backups found")
            return
        
        for name, metadata in sorted(backups, key=lambda x: x[1].get('created_at', '')):
            created_at = metadata.get('created_at', 'Unknown')
            components = ', '.join(metadata.get('components', []))
            size = self.get_directory_size(self.backup_dir / name)
            print(f"📦 {name}")
            print(f"   Created: {created_at}")
            print(f"   Components: {components}")
            print(f"   Size: {size}")
            print()
    
    def get_directory_size(self, path: Path) -> str:
        """Get human-readable directory size"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        # Convert to human readable
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.1f} PB"

def main():
    parser = argparse.ArgumentParser(description='Aetherium Backup and Restore Tool')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], 
                       help='Action to perform')
    parser.add_argument('--name', help='Backup name (for backup/restore)')
    
    args = parser.parse_args()
    
    backup_restore = BackupRestore()
    
    if args.action == 'backup':
        backup_restore.create_backup(args.name)
    elif args.action == 'restore':
        if not args.name:
            print("❌ Backup name required for restore")
            sys.exit(1)
        backup_restore.restore_backup(args.name)
    elif args.action == 'list':
        backup_restore.list_backups()

if __name__ == "__main__":
    main()