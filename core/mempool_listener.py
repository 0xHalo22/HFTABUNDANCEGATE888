import asyncio
from core.simulator import simulate_sandwich_bundle
from core.tx_filter import is_valid_tx

async def listen_for_swaps(w3):
    print("🚨 Starting ETH-only HFT sniper live...")
    print("🔌 Connecting to WebSocket provider...")
    print("🔍 Listening for new pending transactions...")

    async for tx in w3.eth.filter("pending").get_new_entries():
        try:
            tx_hash = tx.hex()
            print(f"🔎 Scanning tx: {tx_hash}")
            tx_data = w3.eth.get_transaction(tx_hash)

            if is_valid_tx(tx_data):
                print("✅ Valid tx detected — sending to execution")
                await simulate_sandwich_bundle(tx_data, w3)
            else:
                print("⛔️ Skipped tx")

        except Exception as e:
            print(f"❌ Error processing tx {tx.hex()}: {e}")
