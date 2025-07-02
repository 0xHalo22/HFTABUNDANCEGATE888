from dotenv import load_dotenv
from core.mempool_listener import listen_for_swaps

load_dotenv()  # Load your .env variables (like ALCHEMY_WSS)

if __name__ == "__main__":
    try:
        print("🚨 Starting ETH-only HFT sniper sim...")
        listen_for_swaps(simulate=True)
    except Exception as e:
        print(f"❌ Error during sniper sim execution: {e}")
