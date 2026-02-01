import time
import sys
from pod_manager import EphemeralPod
from chat_client import start_client
from colorama import init, Fore, Style

init() # Color init

def main():
    print(Fore.CYAN + "=== VISA DENIED: Model Viability Tester ===" + Style.RESET_ALL)
    print("This script will:")
    print("1. Boot a real GPU Pod (RTX A5000 / 4090) on RunPod.")
    print("2. Connect your microphone.")
    print("3. Let you chat with 'Tom' (Immigration Officer).")
    print("4. AUTO-KILL the pod when you exit.")
    
    confirm = input("Ready to spend ~$0.45/hr (A5000) - $0.70/hr (4090)? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    # Initialize safety wrapper
    # Our Gold Image with baked-in model weights (Instant Boot!)
    IMAGE = "matthewkode/personaplex:v2" 
    
    try:
        with EphemeralPod(image_name=IMAGE) as pod:
            if not pod.pod_id:
                print(Fore.RED + "Failed to get Pod ID." + Style.RESET_ALL)
                return
            
            # WAIT loop for service to actually be up (Pod running != App running)
            print("⏳ Waiting extra 45s for Model Loading (Large Model Cold Boot)...")
            # We spin-wait or just sleep.
            time.sleep(45) 
            
            websocket_url = pod.get_endpoint()
            print(Fore.GREEN + f"🔗 Connecting to: {websocket_url}" + Style.RESET_ALL)
            
            print(Fore.YELLOW + "Press Ctrl+C to End Chat and KILL POD." + Style.RESET_ALL)
            time.sleep(2)
            
            # Launch Client
            if websocket_url:
                start_client(websocket_url)
            else:
                print(Fore.RED + "Could not determine socket URL." + Style.RESET_ALL)
                pod.debug_info()
            
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "Interrupted by User." + Style.RESET_ALL)
        # We can't readily access 'pod' here due to scope, but usually we see debug info above if it failed.
    except Exception as e:
        print(f"\n❌ Error: {e}")
        # If we failed inside the block, we might want debug info.
        # But 'pod' variable scope is tricky in try/except blocks in Python if defined in __enter__.
        # Actually, 'pod' is defined.
        try:
             # This is a bit hacky to find the pod object if possible, but let's rely on the inner failure printing it.
             pass
        except:
            pass
    
    # __exit__ should run here automatically
    print(Fore.CYAN + "=== Test Finished. Pod should be dead. ===" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
