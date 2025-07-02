import asyncio
import os
from dotenv import load_dotenv
from web3 import Web3
from core.mempool_listener import listen_for_swaps

load_dotenv()

if __name__ == "__main__":
    try:
        print("🚨 Starting ETH-only HFT sniper live...")

        # Connect to Alchemy via WebSocket
        w3 = Web3(Web3.WebsocketProvider(os.getenv("ALCHEMY_WSS")))

        # Start event loop
        asyncio.run(listen_for_swaps(w3))

    except Exception as e:
        print(f"❌ Error during sniper execution: {e}")
