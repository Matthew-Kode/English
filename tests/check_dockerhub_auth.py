"""
Test Docker Hub credentials locally.
If this works, use the same username/password in your GitHub Secrets.

NOTE: GitHub Secrets cannot be read via API - they're write-only for security.
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

def test_docker_hub_auth(username: str, password: str) -> bool:
    """Test Docker Hub credentials using docker login command."""
    
    try:
        # Use docker login with stdin to test credentials
        result = subprocess.run(
            ["docker", "login", "-u", username, "--password-stdin"],
            input=password,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Logout to clean up
            subprocess.run(["docker", "logout"], capture_output=True)
            return True
        else:
            print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False


def main():
    print("🐳 Docker Hub Credential Tester")
    print("=" * 40)
    
    # Try from .env first
    username = os.getenv("DOCKER_USERNAME")
    password = os.getenv("DOCKER_PASSWORD")
    
    if username and password:
        print(f"\n📋 Testing credentials from .env:")
        print(f"   Username: {username}")
        print(f"   Password: {password[:8]}...{password[-4:] if len(password) > 12 else '****'}")
        
        print("\n🔐 Testing with docker login...")
        if test_docker_hub_auth(username, password):
            print("\n✅ Docker Hub credentials are VALID!")
            print("\n📝 Copy these to GitHub Secrets:")
            print(f"   DOCKER_USERNAME = {username}")
            print(f"   DOCKER_PASSWORD = {password}")
            return True
        else:
            print("\n❌ Docker Hub credentials are INVALID!")
            return False
    else:
        print("\n⚠️ DOCKER_USERNAME and/or DOCKER_PASSWORD not found in .env")
        print("\nAdd these to your .env file:")
        print("   DOCKER_USERNAME=matthewkode")
        print("   DOCKER_PASSWORD=<your Docker Hub Access Token>")
        print("\nThen run this script again.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
