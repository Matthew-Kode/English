import asyncio
import websockets
import ssl
import sys

# Candidates to try
CANDIDATES = [
    "voice_s0.pt", # We know this fails, but keeping as baseline
    "voice-s0.pt", # Hyphen?
    "s0.pt",       # Short?
    "voice_0.pt",
    "voice-0.pt",
    "speaker_0.pt",
    "voice_e2e_0.pt",
    "voice_e2e_s0.pt",
    "voice-s1.pt"
]

BASE_URL = "wss://hftwk8ik5lj66i-8998.proxy.runpod.net/api/chat"

async def check_voice(filename):
    uri = f"{BASE_URL}?text_prompt=Hi&voice_prompt={filename}&seed=42"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    print(f"🔎 Trying '{filename}'...", end=" ")
    try:
        async with websockets.connect(uri, ssl=ssl_context) as ws:
            # Wait for handshake
            msg = await ws.recv()
            if isinstance(msg, bytes) and msg[0] == 0x00:
                print("✅ SUCCESS! Handshake received.")
                return True
            else:
                print(f"❌ Failed (Invalid Handshake: {msg})")
                return False
    except websockets.exceptions.InvalidStatusCode as e:
        # 404 means the path is wrong, but here we might get 500 or ConnectionClosed if server crashes due to file missing
        print(f"❌ Failed ({e.status_code})")
        return False
    except Exception as e:
        print(f"❌ Failed ({e})")
        return False

async def main():
    print("--- Brute Forcing Voice Filenames ---")
    for name in CANDIDATES:
        if await check_voice(name):
            print(f"\n🎉 FOUND IT! The correct filename is: {name}")
            return
    print("\n😭 None of the candidates worked.")

if __name__ == "__main__":
    asyncio.run(main())
