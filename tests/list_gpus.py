import runpod
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("RUNPOD_API_KEY")

if api_key:
    runpod.api_key = api_key

try:
    gpus = runpod.get_gpus()
    print(f"Found {len(gpus)} GPU configurations.")
    print("-" * 40)
    for gpu in gpus:
        print(f"ID: {gpu.get('id', 'UNKNOWN')}")
        print(f"Name: {gpu.get('displayName', 'UNKNOWN')}")
        min_price = gpu.get('minPrice', 'N/A')
        min_bid = gpu.get('minBidPrice', 'N/A')
        print(f"Price: ${min_bid}/hr (Spot) / ${min_price}/hr (OnDemand)")
        print("-" * 40)
except Exception as e:
    print(f"Error listing GPUs: {e}")
