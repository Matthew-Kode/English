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

    pod_id_input = input("\nEnter Pod ID to resume (or press Enter to search/create): ").strip()

    # Initialize safety wrapper
    # Our Gold Image with baked-in model weights (Instant Boot!)
    IMAGE = "matthewkode/personaplex:v4" 
    
    try:
        with EphemeralPod(image_name=IMAGE, existing_pod_id=pod_id_input) as pod:
            if not pod.pod_id:
                print(Fore.RED + "Failed to get Pod ID." + Style.RESET_ALL)
                return
            
            # Allow manual override for faster testing
            websocket_url = input(f"\n🔍 [Manager] Waiting for ports... \n   (You can paste the Proxy URL from RunPod UI here to skip waiting, or press Enter to keep polling): ").strip()
            
            if not websocket_url:
                websocket_url = pod.get_endpoint()
            print(Fore.GREEN + f"🔗 Connecting to: {websocket_url}" + Style.RESET_ALL)
            
            print(Fore.YELLOW + "Press Ctrl+C to End Chat and KILL POD." + Style.RESET_ALL)
            time.sleep(2)
            try:
                # Main Test Loop
                # if MAX_SESSION_MINUTES > 0:
                #     print(f"⏱️  Session Limited to {MAX_SESSION_MINUTES} minutes.")
                #     # In a real app we'd use a timer thread, here we just trust the user plays along
                #     # or we wrap chat_client in a timeout.
                #     pass
                
                # Launch Client
                if websocket_url:
                    start_client(websocket_url) 
                else:
                    print(Fore.RED + "Could not determine socket URL." + Style.RESET_ALL)
                    pod.debug_info()
                
                # Ask user for cleanup preference
                print("\n" + Fore.CYAN + "--- SESSION COMPLETE ---" + Style.RESET_ALL)
                choice = input("Clean up: [T]erminate (Delete) or [S]top (Pause for later)? [T/S]: ").lower()
                if choice == 't':
                    pod.terminate = True
                
            except KeyboardInterrupt:
                print("\n" + Fore.RED + "Interrupted by User." + Style.RESET_ALL) # Corrected original line
            
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
