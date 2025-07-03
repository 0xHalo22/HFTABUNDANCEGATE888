
import asyncio
import aiohttp
import time
from web3 import Web3

# No-auth builders that accept standard bundles (tested and working)
BUILDERS = {
    "titan": "https://rpc.titanbuilder.xyz",
    "eden": "https://builder0x69.io", 
    "rsync": "https://rsync-builder.xyz",
    "payload": "https://rpc.payload.de",
    "nfactorial": "https://rpc.nfactorial.xyz"
}

async def submit_bundle_to_all_builders(front_tx, victim_tx_hash, back_tx, target_block, coinbase_bribe):
    """Submit bundle to ALL builders simultaneously for maximum inclusion odds"""
    
    # Standard bundle format that all builders accept
    bundle_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_sendBundle",
        "params": [{
            "txs": [front_tx, victim_tx_hash, back_tx],
            "blockNumber": Web3.to_hex(target_block),
            "refundPercent": 90
        }]
    }
    
    print(f"🚀 MULTI-BUILDER BLITZ: Submitting to {len(BUILDERS)} builders simultaneously!")
    
    # Submit to all builders in parallel
    tasks = []
    for builder_name, endpoint in BUILDERS.items():
        task = asyncio.create_task(
            submit_to_single_builder(builder_name, endpoint, bundle_payload)
        )
        tasks.append(task)
    
    # Wait for all submissions
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_submissions = 0
    failed_submissions = 0
    
    for i, (builder_name, endpoint) in enumerate(BUILDERS.items()):
        result = results[i]
        if isinstance(result, Exception):
            failed_submissions += 1
            print(f"❌ {builder_name.upper()}: Exception - {result}")
        elif result.get("success"):
            successful_submissions += 1
            print(f"✅ {builder_name.upper()}: SUBMITTED successfully!")
        else:
            failed_submissions += 1
            print(f"❌ {builder_name.upper()}: Failed - {result.get('error', 'Unknown error')}")
    
    print(f"📊 SUBMISSION RESULTS: {successful_submissions}✅ / {failed_submissions}❌")
    
    # Return summary result
    return {
        "success": successful_submissions > 0,
        "successful_count": successful_submissions,
        "failed_count": failed_submissions,
        "total_builders": len(BUILDERS)
    }

async def submit_to_single_builder(builder_name, endpoint, bundle_payload):
    """Submit bundle to a single builder with timeout and error handling"""
    try:
        timeout = aiohttp.ClientTimeout(total=3)  # 3 second timeout
        
        # Standard validation for all builders
        txs = bundle_payload["params"][0]["txs"]
        for i, tx in enumerate(txs):
            if not isinstance(tx, str) or not tx.startswith("0x"):
                print(f"❌ {builder_name.upper()}: Invalid tx format at index {i}: {type(tx)}")
                return {
                    "success": False,
                    "builder": builder_name,
                    "error": f"Invalid transaction format at index {i}"
                }
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            headers = {"Content-Type": "application/json"}
            
            async with session.post(endpoint, json=bundle_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "builder": builder_name,
                        "response": data
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "builder": builder_name,
                        "error": f"HTTP {response.status}: {error_text[:100]}"
                    }
                    
    except asyncio.TimeoutError:
        return {
            "success": False,
            "builder": builder_name,
            "error": "Timeout (3s)"
        }
    except Exception as e:
        return {
            "success": False,
            "builder": builder_name,
            "error": str(e)
        }

def get_builder_stats():
    """Get statistics about builder performance"""
    return {
        "total_builders": len(BUILDERS),
        "builder_list": list(BUILDERS.keys())
    }
