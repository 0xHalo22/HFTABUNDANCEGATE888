import requests
import json

FLASHBOTS_URL = "https://relay.flashbots.net"

def send_flashbots_bundle(bundle, block_number, w3):
    try:
        payload = {
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

        headers = {"Content-Type": "application/json"}
        response = requests.post(FLASHBOTS_URL, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            return {"success": True, "response": response.json()}
        else:
            return {"success": False, "error": response.text}

    except Exception as e:
        return {"success": False, "error": str(e)}
