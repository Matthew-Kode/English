import runpod
import time
import os
import sys
from dotenv import load_dotenv

# Load key from .env
load_dotenv()
api_key = os.getenv("RUNPOD_API_KEY")

if not api_key:
    # Fallback for manual run if env not set
    # In a real app we might error out, but here we check deeply
    pass 

if api_key:
    runpod.api_key = api_key

class EphemeralPod:
    """
    Context Manager to handle RunPod lifecycle safely.
    ensures kill_pod() is called even if code errors out.
    """
    def __init__(self, image_name="nvidia/personaplex", gpu_type=None, environment_variables=None):
        self.image_name = image_name
        self.gpu_type = gpu_type or os.getenv("RUNPOD_GPU_TYPE", "NVIDIA RTX A5000")
        self.pod_id = None
        self.env_vars = environment_variables or {}

    def __enter__(self):
        print(f"🚀 [Manager] Requesting {self.gpu_type} Pod...")
        try:
            # Note: In real usage, might need to filter for specific cloud type or availability
            pod = runpod.create_pod(
                name="Visa-Denied-Tester",
                image_name=self.image_name,
                gpu_type_id=self.gpu_type,
                cloud_type="SECURE", 
                ports="8998/http", # Correct Protocol port # Correct Protocol port
                env=self.env_vars
            )
            self.pod_id = pod['id']
            print(f"✅ [Manager] Pod Created: {self.pod_id}")
            print("⏳ [Manager] Waiting for Boot (approx 20-30s)...")
            
            # Simple polling for 'RUNNING' status
            # For the MVP validation, we'll let the user wait or implement a status check loop here
            # But normally we just return the object and let the client logic handle the "Ready" check
            return self
            
        except Exception as e:
            print(f"❌ [Manager] Failed to create pod: {e}")
            raise e

    def __exit__(self, exc_type, exc_value, traceback):
        print("\n🛑 [Manager] Context Exit Triggered. Terminating Pod...")
        if self.pod_id:
            try:
                runpod.terminate_pod(self.pod_id)
                print(f"💀 [Manager] Pod {self.pod_id} TERMINATED Successfully.")
            except Exception as e:
                print(f"⚠️ [Manager] FAILED TO TERMINATE POD {self.pod_id}: {e}")
                print("!!! PLEASE RUN force_kill.py IMMEDIATELY !!!")
        else:
            print("msg: No pod was created, nothing to kill.")

    def get_endpoint(self):
        """
        Fetches the REAL public IP and PORT from RunPod API.
        Polls until the pod is actually listed as RUNNING and has keys.
        """
        if not self.pod_id:
            return None
            
        print("🔍 [Manager] Polling for Public IP/Port (this ensures container is ready)...")
        for i in range(20): # Try for 100 seconds (20 * 5s)
            try:
                pod_info = runpod.get_pod(self.pod_id)
                # Check status
                status = None
                if 'runtime' in pod_info and 'status' in pod_info['runtime']:
                    status = pod_info['runtime']['status']
                
                # Check ports
                if 'runtime' in pod_info and 'ports' in pod_info['runtime']:
                    ports = pod_info['runtime']['ports']
                    if ports:
                        for p in ports:
                            # We requested 8998/http, so we look for privatePort 8998
                            if p['privatePort'] == 8998 and p['isIpPublic']:
                                pub_ip = p['publicIp']
                                pub_port = p['publicPort']
                                return f"ws://{pub_ip}:{pub_port}/api/chat"
                
                print(f"   [Polling {i+1}/20] Status: {status} | Waiting for Port Mappings...")
                time.sleep(5)
            except Exception as e:
                print(f"   [Polling] Error: {e}")
                time.sleep(5)
        
        print("❌ [Manager] Timed out waiting for Public IP.")
        # Fallback to proxy if direct fails (though unlikely to work if direct didn't appeared)
        return f"wss://{self.pod_id}-8998.proxy.runpod.net/api/chat"
    
    def debug_info(self):
        """Prints raw pod info for debugging."""
        if not self.pod_id:
            print("No Pod ID to debug.")
            return
        try:
            info = runpod.get_pod(self.pod_id)
            print("\n🔍 [DEBUG] RAW POD INFO:")
            import json
            print(json.dumps(info, indent=2))
        except Exception as e:
            print(f"Failed to get debug info: {e}")
