
import asyncio
import requests
from web3 import Web3

# Builder endpoints
BUILDERS = {
    "titan": "https://rpc.titanbuilder.xyz",
    "bloxroute": "https://mev.api.blxrbdn.com",
    "eden": "https://api.edennetwork.io/v1/bundle",
}

async def submit_to_multiple_builders(front_tx, victim_tx_hash, back_tx, target_block):
    """Submit bundle to multiple builders in parallel for higher inclusion rate"""
    
    results = {}
    tasks = []
    
    for builder_name, endpoint in BUILDERS.items():
        task = asyncio.create_task(
            submit_to_builder(builder_name, endpoint, front_tx, victim_tx_hash, back_tx, target_block)
        )
        tasks.append(task)
    
    # Wait for all submissions to complete
    submissions = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for i, (builder_name, endpoint) in enumerate(BUILDERS.items()):
        result = submissions[i]
        if isinstance(result, Exception):
            results[builder_name] = {"success": False, "error": str(result)}
        else:
            results[builder_name] = result
    
    return results

async def submit_to_builder(builder_name, endpoint, front_tx, victim_tx_hash, back_tx, target_block):
    """Submit bundle to a specific builder"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [{
                "txs": [front_tx, victim_tx_hash, back_tx],
                "blockNumber": Web3.to_hex(target_block),
                "minTimestamp": 0,
                "maxTimestamp": 0,
                "revertingTxHashes": []
            }]
        }
        
        headers = {"Content-Type": "application/json"}
        
        print(f"🚀 Submitting to {builder_name.upper()}...")
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {builder_name.upper()} submission successful!")
            return {"success": True, "response": data, "builder": builder_name}
        else:
            print(f"❌ {builder_name.upper()} submission failed: {response.status_code}")
            return {"success": False, "status_code": response.status_code, "builder": builder_name}
            
    except Exception as e:
        print(f"❌ Error submitting to {builder_name}: {e}")
        return {"success": False, "error": str(e), "builder": builder_name}
