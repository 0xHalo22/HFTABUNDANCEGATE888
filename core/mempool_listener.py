import asyncio
from core.simulator import simulate_sandwich_bundle
from core.tx_filter import is_valid_tx

async def listen_for_swaps(w3):
    print("🚨 Starting ETH-only HFT sniper live...")
    print("🔌 Connecting to WebSocket provider...")
    print("🔍 Listening for new pending transactions...")

    tx_filter = w3.eth.filter("pending")

    while True:
        try:
            pending_tx_hashes = tx_filter.get_new_entries()

            for tx_hash in pending_tx_hashes:
                try:
                    tx = w3.eth.get_transaction(tx_hash)

                    if is_valid_tx(tx):
                        print("🎯 Sending to execution pipeline...")
                        await simulate_sandwich_bundle(tx, w3)

                except Exception as e:
                    print(f"❌ Error fetching tx data: {e}")

            await asyncio.sleep(1)  # Poll interval

        except Exception as e:
            print(f"❌ Error in mempool listener loop: {e}")
            await asyncio.sleep(5)
