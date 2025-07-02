
import requests
import json
from web3 import Web3

# Use Titan Builder (no authentication required)
TITAN_URL = "https://rpc.titanbuilder.xyz"
print(f"🔗 Using Titan Builder: {TITAN_URL}")

def send_bundle_to_titan(front_tx_hex, victim_tx_hash, back_tx_hex, target_block):
    try:
        # Titan Builder bundle format (much simpler!)
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [{
                "txs": [front_tx_hex, victim_tx_hash, back_tx_hex],
                "blockNumber": Web3.to_hex(target_block),
                "minTimestamp": 0,
                "maxTimestamp": 0,
                "revertingTxHashes": []
            }]
        }

        print(f"📦 Titan bundle for block {target_block}")
        print(f"📊 Bundle with {len(payload['params'][0]['txs'])} transactions")
        print(f"  🔗 front_tx: {front_tx_hex[:24]}...")
        print(f"  🔗 victim_tx: {victim_tx_hash}")
        print(f"  🔗 back_tx: {back_tx_hex[:24]}...")

        headers = {
            "Content-Type": "application/json"
        }

        print("🚀 Submitting bundle to Titan Builder...")

        response = requests.post(TITAN_URL, json=payload, headers=headers, timeout=10)

        print(f"📡 Titan response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Bundle submitted successfully to Titan!")
            print(f"📄 Titan response: {result}")
            return {"success": True, "response": result}
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

    except Exception as e:
        print(f"❌ Exception in Titan bundle submission: {e}")
        return {"success": False, "error": str(e)}
