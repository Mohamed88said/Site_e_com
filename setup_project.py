#!/usr/bin/env python3
"""
Setup script for Guinée Makiti E-commerce Platform
This script helps set up the project on Windows with VS Code
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Output: {e.output}")
        return False

def check_python():
    """Check if Python is installed"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python found: {result.stdout.strip()}")
        return True
    except:
        print("❌ Python not found. Please install Python 3.8+")
        return False

def check_git():
    """Check if Git is installed"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        print(f"✅ Git found: {result.stdout.strip()}")
        return True
    except:
        print("❌ Git not found. Please install Git")
        return False

def create_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        return run_command("python -m venv venv", "Creating virtual environment")
    else:
        print("✅ Virtual environment already exists")
        return True

def activate_venv_and_install():
    """Activate virtual environment and install requirements"""
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"
    
    # Install requirements
    return run_command(f"{pip_command} install -r requirements.txt", "Installing Python packages")

def setup_database():
    """Set up the database"""
    if os.name == 'nt':  # Windows
        python_command = "venv\\Scripts\\python"
    else:
        python_command = "venv/bin/python"
    
    commands = [
        (f"{python_command} manage.py makemigrations", "Creating migrations"),
        (f"{python_command} manage.py migrate", "Running migrations"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def create_superuser():
    """Create Django superuser"""
    if os.name == 'nt':  # Windows
        python_command = "venv\\Scripts\\python"
    else:
        python_command = "venv/bin/python"
    
    print("\n🔄 Creating superuser...")
    print("Please enter the superuser details:")
    
    try:
        subprocess.run([python_command, "manage.py", "createsuperuser"], check=True)
        print("✅ Superuser created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error creating superuser")
        return False

def setup_env_file():
    """Set up environment file"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from .env.example")
            print("⚠️  Please edit .env file with your actual configuration")
        else:
            # Create basic .env file
            env_content = """SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# Payment Settings (optional)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
"""
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ Created basic .env file")
    else:
        print("✅ .env file already exists")

def create_media_directories():
    """Create necessary media directories"""
    directories = [
        "media",
        "media/products",
        "media/profiles",
        "media/shops",
        "media/reviews",
        "static/images",
        "static/logos"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created media directories")

def setup_vscode():
    """Set up VS Code configuration"""
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # VS Code settings
    settings = {
        "python.defaultInterpreterPath": "./venv/Scripts/python.exe" if os.name == 'nt' else "./venv/bin/python",
        "python.terminal.activateEnvironment": True,
        "files.associations": {
            "*.html": "html"
        },
        "emmet.includeLanguages": {
            "django-html": "html"
        },
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        "python.formatting.provider": "black"
    }
    
    import json
    with open(vscode_dir / "settings.json", "w") as f:
        json.dump(settings, f, indent=4)
    
    # Launch configuration
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Django",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/manage.py",
                "args": ["runserver"],
                "django": True,
                "justMyCode": True
            }
        ]
    }
    
    with open(vscode_dir / "launch.json", "w") as f:
        json.dump(launch_config, f, indent=4)
    
    print("✅ VS Code configuration created")

def main():
    """Main setup function"""
    print("🚀 Setting up Guinée Makiti E-commerce Platform")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python():
        return False
    
    if not check_git():
        print("⚠️  Git not found, but continuing setup...")
    
    # Setup steps
    steps = [
        (create_virtual_environment, "Virtual Environment"),
        (activate_venv_and_install, "Package Installation"),
        (setup_env_file, "Environment Configuration"),
        (create_media_directories, "Directory Structure"),
        (setup_database, "Database Setup"),
        (setup_vscode, "VS Code Configuration"),
    ]
    
    for step_func, step_name in steps:
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    # Optional superuser creation
    print("\n" + "=" * 50)
    create_superuser_choice = input("Do you want to create a superuser now? (y/n): ").lower()
    if create_superuser_choice == 'y':
        create_superuser()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your configuration")
    print("2. Open the project in VS Code")
    print("3. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
        print("4. Run the development server:")
        print("   python manage.py runserver")
    else:
        print("   source venv/bin/activate")
        print("4. Run the development server:")
        print("   python manage.py runserver")
    print("5. Open http://127.0.0.1:8000 in your browser")
    print("\n📧 Admin panel: http://127.0.0.1:8000/admin/")
    print("🛍️  Main site: http://127.0.0.1:8000/")

if __name__ == "__main__":
    main()