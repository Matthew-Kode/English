"""
Quick script to verify your RunPod API credentials are valid.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    api_key = os.getenv("RUNPOD_API_KEY")
    
    if not api_key:
        print("❌ RUNPOD_API_KEY not found in .env")
        return False
    
    print(f"🔑 API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import runpod
        runpod.api_key = api_key
        
        # Try to list pods - this will fail if credentials are invalid
        print("📡 Pinging RunPod API...")
        pods = runpod.get_pods()
        
        print(f"✅ Credentials VALID!")
        print(f"   Active Pods: {len(pods)}")
        
        if pods:
            print("\n📋 Your current pods:")
            for pod in pods:
                name = pod.get('name', 'Unknown')
                pod_id = pod.get('id', 'Unknown')
                status = pod.get('desiredStatus', 'Unknown')
                print(f"   - {name} ({pod_id}) - {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
