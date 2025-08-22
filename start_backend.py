#!/usr/bin/env python3
"""
Startup script for the Django Process Monitor Backend.
This script sets up the database and starts the development server.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    print("Checking dependencies...")
    
    try:
        import django
        print("✓ Django is installed")
    except ImportError:
        print("✗ Django not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "django"])
        print("✓ Django installed successfully")
    
    try:
        import djangorestframework
        print("✓ Django REST Framework is installed")
    except ImportError:
        print("✗ Django REST Framework not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "djangorestframework"])
        print("✓ Django REST Framework installed successfully")
    
    try:
        import django_cors_headers
        print("✓ Django CORS Headers is installed")
    except ImportError:
        print("✗ Django CORS Headers not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "django-cors-headers"])
        print("✓ Django CORS Headers installed successfully")

def setup_database():
    """Set up the database by running migrations."""
    print("Setting up database...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("✗ Backend directory not found!")
        return False
    
    os.chdir(backend_dir)
    
    try:
        # Run migrations
        print("Running database migrations...")
        subprocess.check_call([sys.executable, "manage.py", "makemigrations"])
        subprocess.check_call([sys.executable, "manage.py", "migrate"])
        
        print("✓ Database setup completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Database setup failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during database setup: {e}")
        return False

def start_server():
    """Start the Django development server."""
    print("Starting Django development server...")
    print("The server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        subprocess.check_call([sys.executable, "manage.py", "runserver"])
    except subprocess.CalledProcessError as e:
        print(f"✗ Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n✓ Server stopped by user")
        return True
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    """Main startup process."""
    print("=" * 50)
    print("Process Monitor - Django Backend Startup")
    print("=" * 50)
    print()
    
    try:
        # Check dependencies
        check_dependencies()
        print()
        
        # Setup database
        if not setup_database():
            print("✗ Failed to setup database. Exiting.")
            sys.exit(1)
        
        print()
        
        # Start server
        start_server()
        
    except KeyboardInterrupt:
        print("\n✗ Startup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Startup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 