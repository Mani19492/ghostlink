"""
Link Locator Setup Script
Run once to prepare the application
"""

import os
import subprocess
import sys
import platform

def main():
    print("\n" + "="*50)
    print("    Link Locator - Setup")
    print("="*50 + "\n")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment
    print("\n[1/3] Setting up virtual environment...")
    try:
        if not os.path.exists('venv'):
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("✅ Virtual environment created")
        else:
            print("✅ Virtual environment already exists")
    except Exception as e:
        print(f"❌ Error creating venv: {e}")
        sys.exit(1)
    
    # Get pip path
    if platform.system() == 'Windows':
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    # Install requirements
    print("\n[2/3] Installing dependencies...")
    try:
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt', '--quiet'], check=True)
        print("✅ Dependencies installed")
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)
    
    # Create database
    print("\n[3/3] Initializing database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Warning: Could not pre-create database: {e}")
        print("    It will be created automatically when you start the app")
    
    print("\n" + "="*50)
    print("    Setup Complete!")
    print("="*50)
    print("\n📝 Next Steps:")
    print("   1. Run: python app.py")
    print("   2. Open: http://localhost:5000/dashboard")
    print("   3. Start shortening links!\n")
    
    # Offer to start the app
    response = input("Would you like to start the application now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        print("\n🚀 Starting Link Locator...\n")
        os.system('python app.py' if sys.platform != 'win32' else 'python app.py')

if __name__ == '__main__':
    main()
