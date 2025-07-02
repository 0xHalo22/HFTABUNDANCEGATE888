import requests
import json
from core.flashbots_auth import sign_flashbots_payload

FLASHBOTS_URL = "https://relay.flashbots.net"

def send_flashbots_bundle(bundle, block_number, w3):
    try:
        # Check if block number is still valid (like the example bot)
        current_block = w3.eth.block_number
        if block_number <= current_block:
            print(f"⚠️ Block {block_number} already passed (current: {current_block})")
            block_number = current_block + 1
            print(f"🔄 Updated target block to: {block_number}")

        # Get current timestamp for realistic timing
        import time
        current_time = int(time.time())
        
        payload_obj = {
            "jsonrpc": "2.0", 
            "id": 1,
            "method": "eth_sendBundle",
            "params": [{
                "txs": bundle,
                "blockNumber": hex(block_number),
                "minTimestamp": current_time,
                "maxTimestamp": current_time + 60,  # 1 minute window
                "revertingTxHashes": []
            }]
        }

        # Canonicalize payload
        canonical_payload = json.dumps(payload_obj, separators=(",", ":"), sort_keys=True)
        
        print(f"📦 Bundle for block {block_number} (current: {current_block})")
        print(f"⏰ Timestamp window: {current_time} - {current_time + 60}")
        
        signature = sign_flashbots_payload(canonical_payload)

        headers = {
            "Content-Type": "application/json",
            "X-Flashbots-Signature": signature
        }

        print("🚀 Submitting bundle to Flashbots...")
        response = requests.post(FLASHBOTS_URL, data=canonical_payload, headers=headers, timeout=10)

        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Bundle submitted successfully!")
            return {"success": True, "response": result}
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

    except Exception as e:
        print(f"❌ Exception in bundle submission: {e}")
        return {"success": False, "error": str(e)}
