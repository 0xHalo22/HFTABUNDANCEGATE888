
import asyncio
import aiohttp
import time
from web3 import Web3

# No-auth builders that accept standard bundles (tested and working)
BUILDERS = {
    "titan": "https://rpc.titanbuilder.xyz",
    "eden": "https://builder0x69.io", 
    "rsync": "https://rsync-builder.xyz"
}

async def submit_bundle_to_all_builders_adaptive(front_tx, victim_tx_hash, back_tx, target_block, coinbase_bribe, priority_fee_wei, max_fee_wei):
    """Submit bundle to ALL builders with adaptive EIP-1559 parameters for maximum inclusion odds"""
    
    # Enhanced bundle format with escalated EIP-1559 params
    bundle_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_sendBundle",
        "params": [{
            "txs": [front_tx, victim_tx_hash, back_tx],
            "blockNumber": Web3.to_hex(target_block),
            "refundPercent": 90,
            "maxPriorityFeePerGas": Web3.to_hex(priority_fee_wei),  # Escalated tip
            "maxFeePerGas": Web3.to_hex(max_fee_wei),  # Escalated max fee
            "coinbaseBribe": Web3.to_hex(coinbase_bribe)  # Direct validator bribe
        }]
    }
    
    print(f"🚀 ADAPTIVE MULTI-BUILDER: Submitting to {len(BUILDERS)} builders with escalated params!")
    
    # Submit to all builders in parallel
    tasks = []
    for builder_name, endpoint in BUILDERS.items():
        task = asyncio.create_task(
            submit_to_single_builder_adaptive(builder_name, endpoint, bundle_payload, target_block)
        )
        tasks.append(task)
    
    # Wait for all submissions
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results with enhanced logging
    successful_submissions = 0
    failed_submissions = 0
    builder_responses = {}
    
    for i, (builder_name, endpoint) in enumerate(BUILDERS.items()):
        result = results[i]
        if isinstance(result, Exception):
            failed_submissions += 1
            print(f"❌ {builder_name.upper()}: Exception - {result}")
            builder_responses[builder_name] = {"error": str(result)}
        elif result.get("success"):
            successful_submissions += 1
            print(f"✅ {builder_name.upper()}: ACCEPTED escalated bundle!")
            builder_responses[builder_name] = result.get("response", {})
        else:
            failed_submissions += 1
            error_msg = result.get("error", "Unknown error")
            print(f"❌ {builder_name.upper()}: REJECTED - {error_msg}")
            builder_responses[builder_name] = {"error": error_msg}
    
    print(f"📊 ADAPTIVE RESULTS: {successful_submissions}✅ / {failed_submissions}❌")
    
    # Return enhanced summary
    return {
        "success": successful_submissions > 0,
        "successful_count": successful_submissions,
        "failed_count": failed_submissions,
        "total_builders": len(BUILDERS),
        "builder_responses": builder_responses,
        "target_block": target_block,
        "priority_fee_gwei": priority_fee_wei / 1e9,
        "max_fee_gwei": max_fee_wei / 1e9,
        "coinbase_bribe_eth": coinbase_bribe / 1e18
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

async def submit_to_single_builder_adaptive(builder_name, endpoint, bundle_payload, target_block):
    """Submit bundle to a single builder with enhanced logging and error handling"""
    try:
        timeout = aiohttp.ClientTimeout(total=3)  # 3 second timeout
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            headers = {"Content-Type": "application/json"}
            
            # Enhanced logging for debugging
            params = bundle_payload["params"][0]
            priority_fee = int(params.get("maxPriorityFeePerGas", "0x0"), 16) / 1e9
            max_fee = int(params.get("maxFeePerGas", "0x0"), 16) / 1e9
            
            print(f"🚀 {builder_name.upper()}: Block {target_block} | Prio: {priority_fee:.1f} gwei | MaxFee: {max_fee:.1f} gwei")
            
            async with session.post(endpoint, json=bundle_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for errors in response
                    if "error" in data:
                        print(f"❌ {builder_name.upper()} rejected: {data['error']}")
                        return {
                            "success": False,
                            "builder": builder_name,
                            "error": data["error"],
                            "response": data
                        }
                    else:
                        print(f"✅ {builder_name.upper()} accepted bundle.")
                        return {
                            "success": True,
                            "builder": builder_name,
                            "response": data
                        }
                else:
                    error_text = await response.text()
                    print(f"❌ {builder_name.upper()} HTTP {response.status}: {error_text[:200]}")
                    return {
                        "success": False,
                        "builder": builder_name,
                        "error": f"HTTP {response.status}: {error_text[:100]}",
                        "response": {"status": response.status, "text": error_text[:200]}
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

async def submit_to_single_builder(builder_name, endpoint, bundle_payload):
    """Submit bundle to a single builder with timeout and error handling"""
    try:
        timeout = aiohttp.ClientTimeout(total=3)  # 3 second timeout
        
        # Create builder-specific payload variants
        payload_to_send = bundle_payload.copy()
        
        # All remaining builders use standard format
        
        
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            headers = {"Content-Type": "application/json"}
            
            async with session.post(endpoint, json=payload_to_send, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "builder": builder_name,
                        "response": data
                    }
                else:
                    error_text = await response.text()
                    print(f"❌ {builder_name.upper()} HTTP {response.status}: {error_text[:200]}")
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
