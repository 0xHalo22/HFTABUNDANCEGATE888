import requests
import time

FLASHBOTS_RPC_URL = "https://relay.flashbots.net"

def simulate_bundle(bundle, block_number):
    headers = {"Content-Type": "application/json"}
    body = {
        "jsonrpc": "2.0",
        "id": int(time.time()),
        "method": "eth_callBundle",
        "params": [{
            "txs": bundle,  # raw signed txs (hex strings)
            "blockNumber": hex(block_number),
            "stateBlockNumber": "latest"
        }]
    }

    try:
        response = requests.post(FLASHBOTS_RPC_URL, json=body, headers=headers)
        result = response.json()
        if "error" in result:
            return {"error": result["error"]}
        return result["result"]
    except Exception as e:
        return {"error": str(e)}
