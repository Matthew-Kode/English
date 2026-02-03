import time
import sys
from pod_manager import EphemeralPod
from chat_client import start_client
from colorama import init, Fore, Style

init() # Color init

def main():
    print(Fore.CYAN + "=== VISA DENIED: Model Viability Tester ===" + Style.RESET_ALL)
    print("Mode: MANUAL CLEANUP (Pod will keep running on error)")
    
    confirm = input("Ready to spend ~$0.45/hr (A5000) - $0.70/hr (4090)? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    pod_id_input = input("\nEnter Pod ID to resume (or press Enter to search/create): ").strip()

    # Initialize safety wrapper (But we won't use 'with' to keep it running)
    IMAGE = "matthewkode/personaplex:v4" 
    
    manager = EphemeralPod(image_name=IMAGE, existing_pod_id=pod_id_input)
    pod = manager.__enter__() # Manually enter but we won't call __exit__ automatically on error

    if not pod.pod_id:
        print(Fore.RED + "Failed to get Pod ID." + Style.RESET_ALL)
        return
    
    try:
        # Construct Proxy URL automatically
        websocket_url = f"wss://{pod.pod_id}-8998.proxy.runpod.net/api/chat"
        print(Fore.GREEN + f"🔗 Connecting to: {websocket_url}" + Style.RESET_ALL)
        
        print(Fore.YELLOW + "Press Ctrl+C to stop the client. POD WILL KEEP RUNNING." + Style.RESET_ALL)
        time.sleep(1)
        
        # Launch Client
        start_client(websocket_url) 
        
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "Client Stopped by User." + Style.RESET_ALL)
    except Exception as e:
        print(f"\n❌ Client Error: {e}")
    
    print("\n" + Fore.YELLOW + "⚠️  REMINDER: Pod is still running at " + Fore.WHITE + f"https://console.runpod.io/pods" + Style.RESET_ALL)
    print(Fore.CYAN + "=== Test Session Finished ===" + Style.RESET_ALL)

if __name__ == "__main__":
    main()