import asyncio
import websockets
import ssl
import sys

async def test():
    # URL that worked in your browser (converted to wss)
    base_url = "wss://hftwk8ik5lj66i-8998.proxy.runpod.net/api/chat"
    
    # Minimal params
    params = "?text_prompt=Hi&voice_prompt=voice_1.pt&seed=42"
    uri = base_url + params
    
    print(f"--- DEBUG CONNECTION ---")
    print(f"Target: {uri}")
    
    # Create SSL context that ignores cert errors
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Add User-Agent to mimic Chrome (RunPod Proxy often blocks scripts)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://hftwk8ik5lj66i-8998.proxy.runpod.net"
    }

    try:
        print("Attempting to connect with Browser Headers...")
        async with websockets.connect(uri, ssl=ssl_context, extra_headers=headers) as ws:
            print(f"✅ SUCCESS! WebSocket Connected.")
            await ws.send(b'\x00') # Send handshake
            print("Sent handshake.")
            resp = await ws.recv()
            print(f"Received response: {resp}")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test())