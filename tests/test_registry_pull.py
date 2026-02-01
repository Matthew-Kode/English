"""
Quick test to verify RunPod can pull from your private Docker registry.
Creates a pod, checks if image pull succeeds, then immediately kills it.
Cost: ~$0.01 (less than 1 minute of GPU time)
"""
import os
import sys
import time
import runpod
from dotenv import load_dotenv

load_dotenv()

def test_private_registry_pull():
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ RUNPOD_API_KEY not found")
        return False
    
    runpod.api_key = api_key
    
    # Your private image
    image = "matthewkode/personaplex:v1"
    template_id = os.getenv("RUNPOD_PRIVATE_TEMPLATE_ID")
    
    print(f"🐳 Testing private registry pull: {image}")
    print(f"📋 Using template: {template_id or 'None'}")
    print()
    
    try:
        # Create pod with minimal config
        pod_args = {
            "name": "Registry-Auth-Test",
            "image_name": image,
            "gpu_type_id": "NVIDIA RTX A5000",  # Cheapest available
            "cloud_type": "SECURE",
            "ports": "8998/http",
        }
        
        if template_id:
            pod_args["template_id"] = template_id
        
        print("🚀 Creating test pod...")
        pod = runpod.create_pod(**pod_args)
        pod_id = pod['id']
        print(f"✅ Pod created: {pod_id}")
        
        # Wait a bit for container to start (or fail)
        print("⏳ Waiting 15 seconds for container status...")
        time.sleep(15)
        
        # Check pod status
        print("🔍 Checking pod status...")
        pod_status = runpod.get_pod(pod_id)
        
        runtime = pod_status.get('runtime', {})
        container = runtime.get('container', {}) if runtime else {}
        
        print(f"   Pod Status: {pod_status.get('desiredStatus', 'Unknown')}")
        print(f"   Runtime: {runtime}")
        
        # Try to get logs (if available)
        # Note: RunPod SDK might not have direct log access
        
        # Kill the pod immediately
        print("💀 Terminating test pod...")
        runpod.terminate_pod(pod_id)
        print("✅ Pod terminated")
        
        # Determine result
        if runtime and container:
            print("\n✅ SUCCESS! Private registry pull worked!")
            return True
        else:
            print("\n⚠️ Pod created but container status unclear.")
            print("   Check RunPod console for logs.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_private_registry_pull()
    sys.exit(0 if success else 1)
