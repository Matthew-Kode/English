import asyncio
import websockets
import sounddevice as sd
import numpy as np
import json
import time
import sys
import threading
from collections import deque
import urllib.parse

# config
RATE = 24000  # PersonaPlex/Moshi default
CHANNELS = 1
DTYPE = 'int16' 
BLOCK_SIZE = 1024

class AudioClient:
    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.running = True
        self.send_queue = deque()
        
    async def send_audio(self, ws):
        """Reads from Mic and sends to WS"""
        print("🎙️  Microphone Active. Speak now!")
        
        loop = asyncio.get_event_loop()

        def mic_callback(indata, frames, time_info, status):
            if status:
                print(f"[Mic Error]: {status}")
            if self.running:
                # indata is numpy array (frames, channels)
                # We need raw bytes for the server
                bytes_data = indata.tobytes()
                # Thread-safe queue append? 
                # Deque is thread-safe for appends from ends
                self.send_queue.append(bytes_data)

        # Start input stream
        with sd.InputStream(samplerate=RATE, 
                            channels=CHANNELS, 
                            dtype=DTYPE, 
                            blocksize=BLOCK_SIZE,
                            callback=mic_callback):
            
            while self.running:
                if self.send_queue:
                    data = self.send_queue.popleft()
                    try:
                        # Prepend \x01 for Audio Kind
                        await ws.send(b'\x01' + data)
                    except websockets.exceptions.ConnectionClosed:
                        print("⚠️ Connection closed during send.")
                        break
                else:
                    await asyncio.sleep(0.001)

    async def receive_audio(self, ws):
        """Receives from WS and plays to Speaker"""
        print("🔊 Speaker Active.")
        
        # Output stream
        # buffersize=0 -> let backend choose optimal buffer
        stream = sd.OutputStream(samplerate=RATE, 
                                 channels=CHANNELS, 
                                 dtype=DTYPE)
        stream.start()
        
        try:
            async for message in ws:
                if not self.running:
                    break
                
                if isinstance(message, bytes):
                    kind = message[0]
                    payload = message[1:]

                    if kind == 1: # Audio
                        # Convert bytes back to numpy for sounddevice
                        audio_chunk = np.frombuffer(payload, dtype=np.int16)
                        stream.write(audio_chunk)
                        
                    elif kind == 2: # Text
                        try:
                            text = payload.decode('utf-8')
                            print(f"{text}", end="", flush=True)
                        except: 
                            pass
                    elif kind == 0:
                        print("\n[Handshake Received]")
                        
                elif isinstance(message, str):
                   print(f"\n[Str Message]: {message}", end="", flush=True)

        except websockets.exceptions.ConnectionClosed:
            print("⚠️ Connection closed by server.")
        except Exception as e:
            print(f"❌ Receive Error: {e}")
        finally:
            stream.stop()
            stream.close()

    async def run(self):
        # Query Params for Persona
        params = {
            "text_prompt": "You are Tom, a strict US Immigration Officer. You are suspicious of the traveler. Initiate the conversation first. Interrupt them if they stutter.",
            "voice_prompt": "voice_1.pt", 
            "seed": "42"
        }
        query_string = urllib.parse.urlencode(params)
        full_uri = f"{self.base_uri}?{query_string}"

        print(f"🔌 Connecting to {full_uri}...")
        
        # Retry loop for initial connection (startup delay due to GCC install)
        try:
            while self.running:
                try:
                    async with websockets.connect(full_uri) as ws:
                        print("✅ Connected!")
                        
                        # Run send/recv in parallel
                        await asyncio.gather(
                            self.send_audio(ws),
                            self.receive_audio(ws)
                        )
                        # If we exit gather usually means connection closed or self.running is False
                        if not self.running:
                            break
                            
                except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError) as e:
                    print(f"⏳ Service not ready yet... Retrying in 5s. ({e})")
                    time.sleep(5)
                except Exception as e:
                    print(f"❌ Client Error: {e}")
                    break
        finally:
            self.running = False


def start_client(uri):
    client = AudioClient(uri)
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\n👋 Client stopping...")
        client.running = False
