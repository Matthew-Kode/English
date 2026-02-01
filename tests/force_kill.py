import runpod
import os
from dotenv import load_dotenv

# Load env
load_dotenv()
api_key = os.getenv("RUNPOD_API_KEY")

if not api_key:
    print("❌ Error: RUNPOD_API_KEY not found in .env or environment.")
    # Attempt to ask user? No, just exit.
    exit(1)

runpod.api_key = api_key

def nuke_all():
    print("☢️  INITIATING NUCLEAR OPTION...")
    
    try:
        pods = runpod.get_pods()
        if not pods:
            print("✅ No active pods found. You are safe.")
            return

        print(f"⚠️  Found {len(pods)} active pods!")
        
        for pod in pods:
            pid = pod['id']
            name = pod.get('name', 'Unknown')
            print(f"🔪 Terminating {name} ({pid})...")
            runpod.terminate_pod(pid)
            print(f"   -> Killed {pid}")

        print("\n✅ All pods terminated.")

    except Exception as e:
        print(f"❌ Error listing/killing pods: {e}")
        print("Please check RunPod console manually: https://www.runpod.io/console/pods")

if __name__ == "__main__":
    confirm = input("Are you sure you want to KILL ALL PODS? (y/n): ")
    if confirm.lower() == 'y':
        nuke_all()
    else:
        print("Aborted.")
