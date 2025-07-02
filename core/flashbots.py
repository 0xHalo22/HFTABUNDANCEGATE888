import requests
import json
from core.flashbots_auth import sign_flashbots_payload

FLASHBOTS_URL = "https://relay.flashbots.net"

def send_flashbots_bundle(bundle, block_number, w3):
    try:
        payload_obj = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [{
                "txs": bundle,
                "blockNumber": hex(block_number),
                "minTimestamp": 0,
                "maxTimestamp": 9999999999,
                "revertingTxHashes": []
            }]
        }

        # Canonicalize once and reuse for both signature and transmission
        canonical_payload = json.dumps(payload_obj, separators=(",", ":"))

        # DEBUG: print raw payload and signature
        print("📦 Canonical payload string:")
        print(repr(canonical_payload))
        signature = sign_flashbots_payload(canonical_payload)
        print("🧬 Flashbots Signature Header:")
        print(signature)

        headers = {
            "Content-Type": "application/json",
            "X-Flashbots-Signature": signature
        }

        response = requests.post(FLASHBOTS_URL, data=canonical_payload, headers=headers)

        if response.status_code == 200:
            return {"success": True, "response": response.json()}
        else:
            return {"success": False, "error": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}
