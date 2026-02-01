"""
Check if your Container Registry Auth (Docker credentials) in RunPod is valid.
This verifies the credentials you've stored in RunPod for pulling private images.
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def main():
    api_key = os.getenv("RUNPOD_API_KEY")
    
    if not api_key:
        print("❌ RUNPOD_API_KEY not found in .env")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # RunPod REST API endpoint for container registry auth
    url = "https://rest.runpod.io/v1/containerregistryauth"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Fetching Container Registry Auth credentials from RunPod...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                print("⚠️ No Container Registry credentials found in your RunPod account.")
                print("   → Go to RunPod Settings > Container Registry Auth to add them.")
                return False
            
            print(f"✅ Found {len(data)} credential(s):\n")
            for cred in data:
                cred_id = cred.get('id', 'N/A')
                name = cred.get('name', 'Unnamed')
                username = cred.get('username', 'N/A')
                print(f"   📦 {name}")
                print(f"      ID: {cred_id}")
                print(f"      Username: {username}")
                print(f"      (Full data: {cred})")
                print()
            
            # Check if RUNPOD_REGISTRY_AUTH_ID in .env matches any
            env_auth_id = os.getenv("RUNPOD_REGISTRY_AUTH_ID")
            if env_auth_id:
                match = any(c.get('id') == env_auth_id for c in data)
                if match:
                    print(f"✅ Your .env RUNPOD_REGISTRY_AUTH_ID ({env_auth_id}) matches a saved credential!")
                else:
                    print(f"⚠️ Your .env RUNPOD_REGISTRY_AUTH_ID ({env_auth_id}) does NOT match any saved credential!")
            
            return True
            
        elif response.status_code == 401:
            print("❌ Unauthorized - Invalid API Key")
            return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
