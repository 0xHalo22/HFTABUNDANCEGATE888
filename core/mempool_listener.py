import os
import time
from web3 import Web3
from web3.providers.websocket import WebsocketProvider
from core.tx_filter import is_sandwich_candidate
from core.simulator import simulate_sandwich_bundle

ALCHEMY_WSS = os.getenv("ALCHEMY_WSS")

def listen_for_swaps(simulate=False):
    print("🔌 Connecting to WebSocket provider...")
    w3 = Web3(WebsocketProvider(ALCHEMY_WSS))

    seen = set()
    print("🔍 Listening for new pending transactions...")

    while True:
        try:
            pending_tx_hashes = w3.eth.get_block('pending')['transactions']

            for tx_hash in pending_tx_hashes:
                if tx_hash.hex() in seen:
                    continue
                seen.add(tx_hash.hex())

                try:
                    tx = w3.eth.get_transaction(tx_hash)
                    print(f"🔎 Scanning tx: {tx['hash'].hex()}")  # Debug print

                    if is_sandwich_candidate(tx, w3):
                        print(f"🧠 Victim found: {tx['hash'].hex()}")
                        simulate_sandwich_bundle(tx, w3)
                except Exception:
                    continue

            time.sleep(1)  # Adjust to control polling frequency
        except Exception as e:
            print(f"⚠️ Error polling mempool: {e}")
            time.sleep(3)
