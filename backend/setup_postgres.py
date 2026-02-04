#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Voice of TN
This script helps you set up PostgreSQL database and user
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def setup_postgresql():
    """Set up PostgreSQL database and user"""
    print("🚀 Voice of TN - PostgreSQL Setup")
    print("=" * 40)

    # Check if PostgreSQL is installed
    if not run_command("psql --version", "Checking PostgreSQL installation"):
        print("\n❌ PostgreSQL is not installed!")
        print("Please install PostgreSQL first:")
        print("1. Download from: https://www.postgresql.org/download/windows/")
        print("2. Install with default settings")
        print("3. Run this script again")
        return False

    # Get database credentials from user
    print("\n📝 Database Configuration:")
    db_user = input("Enter PostgreSQL username (default: postgres): ").strip() or "postgres"
    db_password = input("Enter PostgreSQL password: ").strip()
    db_name = input("Enter database name (default: voiceoftn): ").strip() or "voiceoftn"

    if not db_password:
        print("❌ Password is required!")
        return False

    # Update .env file
    env_content = f"""# Database Configuration
DATABASE_URL=postgresql://{db_user}:{db_password}@localhost:5432/{db_name}

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""

    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file updated successfully")
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

    # Create database
    create_db_command = f'psql -U {db_user} -h localhost -c "CREATE DATABASE {db_name};"'
    if run_command(create_db_command, f"Creating database '{db_name}'"):
        print(f"\n🎉 PostgreSQL setup completed successfully!")
        print(f"Database: {db_name}")
        print(f"User: {db_user}")
        print(f"Connection: localhost:5432")
        return True
    else:
        print("\n❌ Database creation failed!")
        print("Make sure PostgreSQL is running and you have the correct credentials.")
        return False

if __name__ == "__main__":
    success = setup_postgresql()
    if success:
        print("\n🚀 You can now run the backend with:")
        print("python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
    else:
        print("\n❌ Setup failed. Please check the errors above and try again.")
        sys.exit(1)