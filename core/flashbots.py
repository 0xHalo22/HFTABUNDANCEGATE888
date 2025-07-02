
import requests
import json
from core.flashbots_auth import sign_flashbots_payload

# Use MEV-Share (no registration required!)
FLASHBOTS_URL = "https://relay.flashbots.net"
print(f"🔗 Using MEV-Share: {FLASHBOTS_URL}")

def send_flashbots_bundle(bundle, block_number, w3):
    try:
        # Check if block number is still valid
        current_block = w3.eth.block_number
        if block_number <= current_block:
            print(f"⚠️ Block {block_number} already passed (current: {current_block})")
            block_number = current_block + 1
            print(f"🔄 Updated target block to: {block_number}")

        # MEV-Share bundle format (simpler!)
        payload_dict = {
            "jsonrpc": "2.0", 
            "id": 1,
            "method": "mev_sendBundle",  # MEV-Share method
            "params": [{
                "version": "v0.1",
                "inclusion": {
                    "block": hex(block_number),
                    "maxBlock": hex(block_number + 3)  # Allow inclusion in next 3 blocks
                },
                "body": bundle
            }]
        }

        print(f"📦 Bundle for block {block_number} (current: {current_block})")
        print(f"⏰ Timestamp window: {current_time} - {current_time + 60}")
        
        # Use the fixed signature function
        header_value, canonical_json = sign_flashbots_payload(payload_dict)

        headers = {
            "Content-Type": "application/json",
            "X-Flashbots-Signature": header_value
        }

        print("🚀 Submitting bundle to Flashbots...")
        
        # Critical: Use data= not json= to prevent reserialization
        response = requests.post(FLASHBOTS_URL, data=canonical_json, headers=headers, timeout=10)

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
