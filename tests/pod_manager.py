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
    def __init__(self, image_name="matthewkode/personaplex:v4", gpu_type=None, environment_variables=None, terminate=False, existing_pod_id=None):
        self.image_name = image_name
        self.gpu_type = gpu_type or os.getenv("RUNPOD_GPU_TYPE", "NVIDIA RTX A5000")
        self.pod_id = existing_pod_id
        self.terminate = terminate
        self.env_vars = environment_variables or {}
        # Re-enabling torch.compile since v3 image has build-essential
        self.env_vars["NO_TORCH_COMPILE"] = "0" 
        self.env_vars["MOSHI_USE_CUDA_GRAPH"] = "1"
        if os.getenv("HF_TOKEN"):
            self.env_vars["HF_TOKEN"] = os.getenv("HF_TOKEN")
        
        # Docker Hub credentials for private registry
        self.docker_username = os.getenv("DOCKER_USERNAME")
        self.docker_password = os.getenv("DOCKER_PASSWORD")

    def __enter__(self):
        print(f"🚀 [Manager] Searching for pod to resume...")
        cache_file = ".last_pod_id"
        try:
            # 1. Verification Logic
            existing_pods = runpod.get_pods()
            target_pod = None
            
            # Use provided ID first
            if self.pod_id:
                target_pod = next((p for p in existing_pods if p['id'] == self.pod_id), None)
                if not target_pod:
                    print(f"⚠️ [Manager] Provided ID {self.pod_id} not found. Searching elsewhere...")
            
            # Use local cache file second
            if not target_pod and os.path.exists(cache_file):
                with open(cache_file, "r") as f:
                    cached_id = f.read().strip()
                    target_pod = next((p for p in existing_pods if p['id'] == cached_id), None)
            
            # Fallback to name search third
            if not target_pod:
                target_pod = next((p for p in existing_pods if p.get('name') == "Visa-Denied-Tester"), None)

            if target_pod:
                self.pod_id = target_pod['id']
                print(f"♻️ [Manager] Resuming pod {self.pod_id}...")
                with open(cache_file, "w") as f: f.write(self.pod_id) # Update cache
                
                status = target_pod.get('status') or (target_pod.get('runtime') or {}).get('status')
                if status != 'RUNNING':
                    runpod.resume_pod(self.pod_id, gpu_count=target_pod.get('gpuCount', 1))
                return self

            # 3. Create new if none found
            pod_args = {
                "name": "Visa-Denied-Tester",
                "image_name": self.image_name,
                "gpu_type_id": self.gpu_type,
                "cloud_type": "SECURE",
                "ports": "8998/http",
                "volume_in_gb": 20,
                "env": self.env_vars
            }
            
            # Use template_id if available (for private registry with pre-configured auth)
            template_id = os.getenv("RUNPOD_PRIVATE_TEMPLATE_ID")
            if template_id:
                pod_args["template_id"] = template_id
                print(f"🔐 [Manager] Using template {template_id} for private registry.")
            
            pod = runpod.create_pod(**pod_args)
            self.pod_id = pod['id']
            with open(cache_file, "w") as f: f.write(self.pod_id) # Save to cache
            print(f"✅ [Manager] Pod Created: {self.pod_id}")
            return self
            
        except Exception as e:
            print(f"❌ [Manager] Failed to create pod: {e}")
            raise e

    def __exit__(self, exc_type, exc_value, traceback):
        print("\n🛑 [Manager] Context Exit Triggered. Cleaning up Pod...")
        cache_file = ".last_pod_id"
        if self.pod_id:
            try:
                if self.terminate:
                    runpod.terminate_pod(self.pod_id)
                    if os.path.exists(cache_file):
                        os.remove(cache_file)
                    print(f"💀 [Manager] Pod {self.pod_id} TERMINATED Successfully.")
                else:
                    runpod.stop_pod(self.pod_id)
                    print(f"⏸️ [Manager] Pod {self.pod_id} STOPPED (Paused) Successfully.")
            except Exception as e:
                action = "TERMINATE" if self.terminate else "STOP"
                print(f"⚠️ [Manager] FAILED TO {action} POD {self.pod_id}: {e}")
        else:
            print("msg: No pod was created, nothing to kill.")

    def get_endpoint(self):
        """
        Returns the Proxy URL as soon as the pod is RUNNING.
        """
        if not self.pod_id:
            return None
            
        print(f"🔍 [Manager] Waiting for pod {self.pod_id} to be RUNNING...")
        proxy_url = f"wss://{self.pod_id}-8998.proxy.runpod.net/api/chat"
        
        attempt = 0
        while True:
            attempt += 1
            try:
                pod_status = runpod.get_pod(self.pod_id)
                if not pod_status:
                    time.sleep(5)
                    continue

                # Check status across all possible API fields
                status = (pod_status.get('status') or 
                          pod_status.get('podStatus') or 
                          (pod_status.get('runtime') or {}).get('status'))
                
                if status == 'RUNNING':
                    print(f"✅ [Manager] Pod is RUNNING. Connecting to Proxy...")
                    return proxy_url
                
                print(f"   [Polling #{attempt}] Status: {status}...")
                time.sleep(5)
            except Exception as e:
                print(f"   [Polling] Note: {e}")
                time.sleep(5)
    
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
