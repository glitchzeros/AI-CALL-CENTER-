#!/usr/bin/env python3
"""
Aetherium Development Environment Setup Script
Automated setup for development environment
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import List, Tuple

class DevSetup:
    def __init__(self):
        self.project_root = Path("/workspace/Ozodbek-")
        self.requirements_installed = False
        
    def check_system_requirements(self) -> List[Tuple[bool, str]]:
        """Check if system requirements are met"""
        results = []
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                results.append((True, f"✅ Docker: {result.stdout.strip()}"))
            else:
                results.append((False, "❌ Docker not found"))
        except FileNotFoundError:
            results.append((False, "❌ Docker not installed"))
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                results.append((True, f"✅ Docker Compose: {result.stdout.strip()}"))
            else:
                results.append((False, "❌ Docker Compose not found"))
        except FileNotFoundError:
            results.append((False, "❌ Docker Compose not installed"))
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                results.append((True, f"✅ Python: {result.stdout.strip()}"))
            else:
                results.append((False, "❌ Python not found"))
        except FileNotFoundError:
            results.append((False, "❌ Python not installed"))
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                results.append((True, f"✅ Node.js: {result.stdout.strip()}"))
            else:
                results.append((False, "❌ Node.js not found"))
        except FileNotFoundError:
            results.append((False, "❌ Node.js not installed"))
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                results.append((True, f"✅ npm: {result.stdout.strip()}"))
            else:
                results.append((False, "❌ npm not found"))
        except FileNotFoundError:
            results.append((False, "❌ npm not installed"))
        
        return results
    
    def setup_environment_files(self) -> bool:
        """Setup environment configuration files"""
        try:
            print("⚙️ Setting up environment files...")
            
            env_example = self.project_root / ".env.example"
            env_file = self.project_root / ".env"
            
            if env_example.exists() and not env_file.exists():
                shutil.copy(env_example, env_file)
                print("✅ Created .env from .env.example")
                
                # Update with development-friendly defaults
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Replace placeholder values with development defaults
                replacements = {
                    'your_secure_password_here': 'dev_password_123',
                    'your_very_secure_jwt_secret_key_here_minimum_32_characters': 'dev_jwt_secret_key_for_development_use_only_32_chars',
                    'your_32_character_encryption_key_here': 'dev_encryption_key_32_characters_',
                    'your_gemini_api_key_here': 'demo_gemini_key_replace_with_real',
                    'your_telegram_bot_token_here': 'demo_telegram_token_replace_with_real',
                    'your_sms_api_key_here': 'demo_sms_key_replace_with_real'
                }
                
                for old, new in replacements.items():
                    content = content.replace(old, new)
                
                with open(env_file, 'w') as f:
                    f.write(content)
                
                print("✅ Updated .env with development defaults")
            elif env_file.exists():
                print("✅ .env file already exists")
            else:
                print("❌ .env.example not found")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Environment setup error: {e}")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies for development tools"""
        try:
            print("🐍 Installing Python development dependencies...")
            
            # Install common development packages
            dev_packages = [
                'aiohttp',
                'psutil',
                'requests'
            ]
            
            for package in dev_packages:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"  ✅ Installed: {package}")
                else:
                    print(f"  ⚠️ Failed to install {package}: {result.stderr}")
            
            self.requirements_installed = True
            return True
            
        except Exception as e:
            print(f"❌ Python dependencies installation error: {e}")
            return False
    
    def setup_git_hooks(self) -> bool:
        """Setup Git hooks for development"""
        try:
            print("🔗 Setting up Git hooks...")
            
            hooks_dir = self.project_root / ".git" / "hooks"
            if not hooks_dir.exists():
                print("⚠️ Git repository not found, skipping hooks setup")
                return True
            
            # Pre-commit hook
            pre_commit_hook = hooks_dir / "pre-commit"
            pre_commit_content = """#!/bin/bash
# Aetherium pre-commit hook

echo "🔍 Running pre-commit checks..."

# Check for large files
find . -size +10M -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./frontend/dist/*" | while read file; do
    echo "⚠️ Large file detected: $file"
done

# Check for sensitive data patterns
if grep -r "password.*=" --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules .; then
    echo "⚠️ Potential password in code detected"
fi

echo "✅ Pre-commit checks completed"
"""
            
            with open(pre_commit_hook, 'w') as f:
                f.write(pre_commit_content)
            
            os.chmod(pre_commit_hook, 0o755)
            print("✅ Pre-commit hook installed")
            
            return True
            
        except Exception as e:
            print(f"❌ Git hooks setup error: {e}")
            return False
    
    def create_development_scripts(self) -> bool:
        """Create helpful development scripts"""
        try:
            print("📝 Creating development scripts...")
            
            scripts_dir = self.project_root / "scripts"
            
            # Quick start script
            quick_start = scripts_dir / "quick_start.sh"
            quick_start_content = """#!/bin/bash
# Quick start script for development

echo "🚀 Quick Start - Aetherium Development"
echo "======================================"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose down

# Start core services only
echo "🔄 Starting core services..."
docker compose up -d database redis backend-api

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check health
echo "🏥 Checking service health..."
curl -f http://localhost:8000/health || echo "❌ Backend not ready"

echo "✅ Core services started!"
echo "🌐 Backend API: http://localhost:8000"
echo "📊 Health Check: http://localhost:8000/health"
echo ""
echo "To start frontend: docker compose up -d web-frontend"
echo "To view logs: docker compose logs -f [service_name]"
"""
            
            with open(quick_start, 'w') as f:
                f.write(quick_start_content)
            os.chmod(quick_start, 0o755)
            
            # Development logs script
            dev_logs = scripts_dir / "dev_logs.sh"
            dev_logs_content = """#!/bin/bash
# Development logs viewer

if [ "$1" = "" ]; then
    echo "📋 Available services:"
    docker compose ps --format "table {{.Service}}\t{{.Status}}"
    echo ""
    echo "Usage: $0 [service_name|all]"
    echo "Example: $0 backend-api"
    echo "Example: $0 all"
    exit 1
fi

if [ "$1" = "all" ]; then
    echo "📊 Showing logs for all services..."
    docker compose logs -f
else
    echo "📊 Showing logs for $1..."
    docker compose logs -f "$1"
fi
"""
            
            with open(dev_logs, 'w') as f:
                f.write(dev_logs_content)
            os.chmod(dev_logs, 0o755)
            
            print("✅ Development scripts created")
            return True
            
        except Exception as e:
            print(f"❌ Development scripts creation error: {e}")
            return False
    
    def setup_vscode_config(self) -> bool:
        """Setup VS Code configuration for development"""
        try:
            print("💻 Setting up VS Code configuration...")
            
            vscode_dir = self.project_root / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            # Settings
            settings = {
                "python.defaultInterpreterPath": "/usr/bin/python3",
                "python.linting.enabled": True,
                "python.linting.pylintEnabled": True,
                "python.formatting.provider": "black",
                "typescript.preferences.quoteStyle": "single",
                "editor.formatOnSave": True,
                "files.exclude": {
                    "**/__pycache__": True,
                    "**/node_modules": True,
                    "**/dist": True,
                    "**/.git": True
                },
                "docker.showStartPage": False
            }
            
            with open(vscode_dir / "settings.json", 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Launch configuration
            launch_config = {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Debug Backend",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/backend/main.py",
                        "console": "integratedTerminal",
                        "env": {
                            "PYTHONPATH": "${workspaceFolder}/backend"
                        }
                    }
                ]
            }
            
            with open(vscode_dir / "launch.json", 'w') as f:
                json.dump(launch_config, f, indent=2)
            
            # Extensions recommendations
            extensions = {
                "recommendations": [
                    "ms-python.python",
                    "ms-vscode.vscode-typescript-next",
                    "bradlc.vscode-tailwindcss",
                    "ms-azuretools.vscode-docker",
                    "ms-vscode.vscode-json",
                    "redhat.vscode-yaml",
                    "esbenp.prettier-vscode"
                ]
            }
            
            with open(vscode_dir / "extensions.json", 'w') as f:
                json.dump(extensions, f, indent=2)
            
            print("✅ VS Code configuration created")
            return True
            
        except Exception as e:
            print(f"❌ VS Code setup error: {e}")
            return False
    
    def run_setup(self):
        """Run complete development setup"""
        print("🚀 Aetherium Development Environment Setup")
        print("=" * 50)
        
        # Check system requirements
        print("\n🔍 Checking system requirements...")
        requirements = self.check_system_requirements()
        for success, message in requirements:
            print(f"  {message}")
        
        failed_requirements = [msg for success, msg in requirements if not success]
        if failed_requirements:
            print(f"\n❌ Missing requirements. Please install:")
            for msg in failed_requirements:
                print(f"  {msg}")
            return False
        
        print("\n✅ All system requirements met!")
        
        # Setup steps
        setup_steps = [
            ("Environment Files", self.setup_environment_files),
            ("Python Dependencies", self.install_python_dependencies),
            ("Git Hooks", self.setup_git_hooks),
            ("Development Scripts", self.create_development_scripts),
            ("VS Code Configuration", self.setup_vscode_config)
        ]
        
        success_count = 0
        for step_name, step_func in setup_steps:
            print(f"\n🔧 {step_name}...")
            if step_func():
                success_count += 1
            else:
                print(f"⚠️ {step_name} setup had issues")
        
        print(f"\n📊 Setup Summary:")
        print(f"  Completed: {success_count}/{len(setup_steps)} steps")
        
        if success_count == len(setup_steps):
            print(f"\n🎉 Development environment setup completed successfully!")
            print(f"\n📋 Next steps:")
            print(f"  1. Review and update .env file with your API keys")
            print(f"  2. Run: ./scripts/quick_start.sh")
            print(f"  3. Open project in VS Code for best experience")
            print(f"  4. Check health: python scripts/health_check.py")
        else:
            print(f"\n⚠️ Setup completed with some issues. Check the output above.")
        
        return success_count == len(setup_steps)

def main():
    setup = DevSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()