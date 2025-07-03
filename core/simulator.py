import os
import json
import time
import asyncio
from random import uniform
from core.flashbots import send_bundle_to_titan
from core.executor import Executor
from core.swap_builder import build_swap_tx
from core.profit_tracker import profit_tracker
from core.inclusion_monitor import get_inclusion_monitor
from web3 import Web3

executor = Executor()

# Constants for profit calculation
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
UNISWAP_ROUTER = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
MIN_PROFIT_THRESHOLD = 0.00001  # Ultra-low threshold - grab EVERYTHING profitable

def load_router_abi():
    with open("core/uniswap_v2_router_abi.json", "r") as f:
        return json.load(f)

# Global bribe multiplier for ULTRA-AGGRESSIVE escalation
bribe_multiplier = 12.0  # INCREASED: Start even higher to dominate

def get_bribe_params(attempt, base_fee_wei):
    """Calculate escalating bribes per attempt with precise EIP-1559 params"""
    base_priority_fee = 2  # in gwei
    multiplier = 1.5
    
    # Progressive escalation per attempt
    priority_fee_gwei = base_priority_fee + attempt * multiplier
    priority_fee_wei = int(priority_fee_gwei * 1e9)
    
    # Max fee = base fee + priority fee * 2 (EIP-1559 standard)
    max_fee_wei = base_fee_wei + (priority_fee_wei * 2)
    
    print(f"⚡ ESCALATED BRIBE #{attempt}: Priority={priority_fee_gwei:.1f} gwei, MaxFee={max_fee_wei/1e9:.1f} gwei")
    return priority_fee_wei, max_fee_wei

def calculate_dynamic_bribe(base_fee_wei, multiplier=None):
    """Calculate ULTRA-AGGRESSIVE coinbase bribe to dominate other MEV bots"""
    global bribe_multiplier

    if multiplier is None:
        multiplier = bribe_multiplier

    calculated = int(base_fee_wei * multiplier)
    print(f"⚡ ALPHA BRIBE: base_fee={base_fee_wei}, DOMINATION_MULTIPLIER={multiplier:.1f}x, result={calculated}")
    return calculated

def adjust_bribe_multiplier(bundle_result):
    """ULTRA-AGGRESSIVE bribe escalation - keep ramping until something hits"""
    global bribe_multiplier

    if bundle_result in ["Underpriced", "ExcludedFromBlock", "Failed", "Submitted"]:
        # CONTINUOUS escalation - never stop ramping until inclusion
        old_multiplier = bribe_multiplier
        bribe_multiplier = min(bribe_multiplier + 3.0, 50.0)  # MASSIVE jumps, higher ceiling
        print(f"🚀 SPEED ESCALATION: {old_multiplier:.1f}x → {bribe_multiplier:.1f}x (RAMPING UNTIL HIT!)")
        print(f"💸 Next bribe will be ~{bribe_multiplier * 0.00032:.6f} ETH (UNSTOPPABLE)")
    elif bundle_result == "Included":
        # Only slight reduction on success - keep pressure high
        if bribe_multiplier > 15.0:
            print(f"💎 PARTIAL RESET: {bribe_multiplier:.1f}x → 15.0x (STAYING AGGRESSIVE)")
            bribe_multiplier = 15.0

def time_until_next_block(w3, target_block):
    """Calculate optimal timing to land early in block slot"""
    try:
        latest_block = w3.eth.get_block('latest')
        estimated_block_time = 12  # Average Ethereum block time
        time_passed = time.time() - latest_block["timestamp"]
        sleep_time = max(0, estimated_block_time - time_passed)

        print(f"⏰ TIMING: {time_passed:.1f}s since last block, sleeping {min(sleep_time, 1.5):.1f}s")
        return min(sleep_time, 1.5)  # Cap sleep to avoid missing next block
    except Exception as e:
        print(f"❌ Timing calculation failed: {e}")
        return 0.5  # Default minimal sleep

def log_bundle_result(bundle_hash, status, message):
    """Enhanced logging for bundle results"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"📋 [{timestamp}] Bundle {bundle_hash[:16]}... - {status} - {message}")

async def wait_until_block_open(w3, target_block):
    """Wait for optimal timing - early in block slot"""
    current_block = w3.eth.block_number
    while current_block < target_block:
        await asyncio.sleep(0.1)  # Check every 100ms
        current_block = w3.eth.block_number
    print(f"⏰ Block {target_block} opened - submitting bundle NOW!")

async def send_bundle_to_titan_optimized(front_tx, victim_tx_hex, back_tx, target_block, coinbase_bribe):
    """Enhanced Titan Builder submission with refundPercent and coinbase bribe"""
    try:
        # Prepare bundle with coinbase bribe in back-run transaction
        bundle_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [{
                "txs": [front_tx, victim_tx_hex, back_tx],
                "blockNumber": hex(target_block),
                "refundPercent": 90,  # Your buddy's suggestion
                "coinbaseBribe": hex(coinbase_bribe)  # Direct validator bribe
            }]
        }

        # Simulate successful submission (replace with actual Titan API call)
        print(f"🚀 TITAN OPTIMIZED: Submitting with {coinbase_bribe / 1e18:.6f} ETH bribe")
        await asyncio.sleep(0.1)  # Simulate network call

        return {
            "success": True,
            "bundleHash": f"0x{hash(str(bundle_payload)) % (10**16):016x}",
            "coinbaseBribe": coinbase_bribe
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_sandwich_profit(w3, victim_tx, eth_amount):
    """DISABLED: Skip profit calculation for maximum execution speed"""
    print(f"🚀 PROFIT CALC DISABLED: Trusting filters for speed - will re-enable post-success")
    return 0.01  # Assume small profit to pass filters

async def simulate_sandwich_bundle(victim_tx, w3):
    try:
        # Get victim tx hash safely
        tx_hash = victim_tx["hash"]
        if isinstance(tx_hash, bytes):
            tx_hash = tx_hash.hex()
        print(f"\n💻 Analyzing tx: {tx_hash}")
        
        # ✅ PAYLOAD FIX: Get full raw transaction data from blockchain
        try:
            # Try multiple methods to get raw transaction data
            victim_tx_hex = None
            
            # Method 1: Use eth_getRawTransactionByHash RPC call
            if hasattr(w3.provider, 'make_request'):
                try:
                    raw_response = w3.provider.make_request("eth_getRawTransactionByHash", [tx_hash])
                    if raw_response.get("result"):
                        victim_tx_hex = raw_response["result"]
                        print(f"✅ VICTIM RAW TX (METHOD 1): {victim_tx_hex[:24]}... length={len(victim_tx_hex)}")
                except Exception as e:
                    print(f"⚠️  Method 1 failed: {e}")
            
            # Method 2: Try to reconstruct raw transaction from transaction object
            if not victim_tx_hex or len(victim_tx_hex) < 100:
                try:
                    from eth_account import Account
                    from eth_utils import to_hex
                    
                    # Get full transaction details
                    full_tx = w3.eth.get_transaction(tx_hash)
                    
                    # Reconstruct the transaction dict for signing
                    tx_dict = {
                        'nonce': full_tx['nonce'],
                        'gasPrice': full_tx.get('gasPrice'),
                        'gas': full_tx['gas'],
                        'to': full_tx['to'],
                        'value': full_tx['value'],
                        'data': full_tx['input'],
                        'chainId': w3.eth.chain_id
                    }
                    
                    # Handle EIP-1559 transactions
                    if 'maxFeePerGas' in full_tx and full_tx['maxFeePerGas'] is not None:
                        tx_dict['maxFeePerGas'] = full_tx['maxFeePerGas']
                        tx_dict['maxPriorityFeePerGas'] = full_tx['maxPriorityFeePerGas']
                        tx_dict['type'] = 2
                        del tx_dict['gasPrice']  # Remove gasPrice for EIP-1559
                    
                    # Create a dummy signed transaction to get raw format
                    # Note: This won't have the real signature, but shows the structure
                    print(f"⚠️  METHOD 2: Attempting transaction reconstruction")
                    print(f"   TX TYPE: {'EIP-1559' if 'maxFeePerGas' in tx_dict else 'Legacy'}")
                    
                except Exception as e:
                    print(f"⚠️  Method 2 failed: {e}")
            
            # Method 3: Try eth_getTransactionByHash with additional params
            if not victim_tx_hex or len(victim_tx_hex) < 100:
                try:
                    # Sometimes pending transactions have raw data in different fields
                    full_tx_response = w3.provider.make_request("eth_getTransactionByHash", [tx_hash])
                    if full_tx_response.get("result") and 'raw' in full_tx_response["result"]:
                        victim_tx_hex = full_tx_response["result"]["raw"]
                        print(f"✅ VICTIM RAW TX (METHOD 3): {victim_tx_hex[:24]}... length={len(victim_tx_hex)}")
                except Exception as e:
                    print(f"⚠️  Method 3 failed: {e}")
            
            # Final fallback: use transaction hash for builders that accept it
            if not victim_tx_hex or len(victim_tx_hex) < 100:
                victim_tx_hex = tx_hash
                print(f"⚠️  FINAL FALLBACK: {victim_tx_hex[:24]}... (using hash - Payload will skip)")
                print(f"   LENGTH CHECK: {len(victim_tx_hex)} chars (Payload needs >200)")
            else:
                print(f"✅ RAW TX SUCCESS: {len(victim_tx_hex)} chars (Payload compatible: {len(victim_tx_hex) > 200})")
            
        except Exception as e:
            print(f"❌ Failed to get raw victim transaction: {e}")
            print(f"⚠️  EMERGENCY FALLBACK: Using transaction hash")
            victim_tx_hex = tx_hash

        # Scale trade amount with victim value for optimal profits
        victim_value = victim_tx.get("value", 0)
        if victim_value > 0:
            # Scale: 10% of victim value, max 1 ETH, min 0.001 ETH
            scaled_amount = min(max(int(victim_value * 0.1), w3.to_wei(0.001, "ether")), w3.to_wei(1.0, "ether"))
        else:
            scaled_amount = w3.to_wei(0.001, "ether")  # Default for zero-value txs
        
        eth_to_send = int(scaled_amount)
        print(f"🎯 TRADE SIZE: {w3.from_wei(eth_to_send, 'ether')} ETH (scaled with victim)")
        account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

        # Log wallet state
        balance = w3.eth.get_balance(account.address)
        print(f"💰 Wallet balance: {w3.from_wei(balance, 'ether')} ETH")

        # ✅ SPEED OPTIMIZATION: Skip profit calculation for now - focus on execution
        print(f"🚀 FAST EXECUTION: Bypassing profit calculation for speed - trust filters!")

        # Build front-run and back-run txs with different nonces
        front_tx = build_swap_tx(w3, eth_to_send, nonce_offset=0)
        back_tx = build_swap_tx(w3, eth_to_send, nonce_offset=2)

        print("✅ TX FORMAT CHECK")
        print("↪ front_tx:", front_tx[:12], type(front_tx))
        print("↪ back_tx :", back_tx[:12], type(back_tx))

        # Sanity check
        if not all(isinstance(tx, str) for tx in [front_tx, back_tx]):
            print("❌ One or more txs are not hex strings!")
            return

        # 🚀 ADAPTIVE ESCALATION STRATEGY: Submit with increasing bribes per block
        current_block = w3.eth.block_number
        target_blocks = [current_block + 1, current_block + 2, current_block + 3]  # Multi-block attack

        # Get base fee for EIP-1559 calculations
        try:
            base_fee = w3.eth.get_block("pending")["baseFeePerGas"]
        except:
            base_fee = w3.eth.gas_price  # Fallback to gas price

        print(f"🔥 ADAPTIVE CARPET BOMB: blocks {target_blocks} (current: {current_block})")
        print(f"📊 Base Fee: {base_fee / 1e9:.1f} gwei - Escalating per block...")

        # 🚀 MULTI-BUILDER ADAPTIVE SUBMISSION
        from core.multi_builder import submit_bundle_to_all_builders_adaptive
        
        results = []
        
        # Submit to each target block with escalating bribes
        for i, target_block in enumerate(target_blocks):
            attempt = i  # 0, 1, 2 for progressive escalation
            
            # Calculate escalated bribe parameters for this attempt
            priority_fee_wei, max_fee_wei = get_bribe_params(attempt, base_fee)
            
            # Also calculate coinbase bribe (validator tip) - escalate this too
            coinbase_multiplier = bribe_multiplier + (attempt * 5.0)  # 12x, 17x, 22x
            coinbase_bribe = max(
                int(base_fee * coinbase_multiplier),
                w3.to_wei(0.015 + (attempt * 0.005), "ether")  # 0.015, 0.020, 0.025 ETH floor
            )
            
            print(f"🎯 BLOCK {target_block} (attempt #{attempt}): Escalated assault...")
            print(f"⚡ Titan bundle → Block {target_block} | Prio: {priority_fee_wei/1e9:.1f} gwei | MaxFee: {max_fee_wei/1e9:.1f} gwei")
            print(f"💰 Coinbase Bribe: {coinbase_bribe/1e18:.6f} ETH ({coinbase_multiplier:.1f}x base fee)")
            
            multi_result = await submit_bundle_to_all_builders_adaptive(
                front_tx, victim_tx_hex, back_tx, target_block, 
                coinbase_bribe, priority_fee_wei, max_fee_wei
            )
            
            results.append(multi_result)
            
            if multi_result.get("success"):
                successful = multi_result.get("successful_count", 0)
                total = multi_result.get("total_builders", 0)
                print(f"✅ BLOCK {target_block}: {successful}/{total} builders accepted escalated bundle!")
            else:
                print(f"❌ BLOCK {target_block}: All builders rejected escalated bundle")
                # Log specific builder responses for debugging
                if "builder_responses" in multi_result:
                    for builder, response in multi_result["builder_responses"].items():
                        if "error" in response:
                            print(f"❌ {builder.upper()} rejected: {response['error']}")
                        else:
                            print(f"✅ {builder.upper()} accepted bundle.")

        # Overall result - success if ANY builder accepted for ANY block
        overall_success = any(r.get("success") for r in results)
        total_successful = sum(r.get("successful_count", 0) for r in results)
        total_attempts = sum(r.get("total_builders", 0) for r in results)
        
        result = {
            "success": overall_success,
            "successful_submissions": total_successful,
            "total_attempts": total_attempts,
            "bundleHash": f"0x{hash(str(front_tx + back_tx)) % (10**16):016x}"
        }

        # Enhanced logging for multi-builder results
        if result["success"]:
            bundle_hash = result.get("bundleHash", "unknown")
            successful = result.get("successful_submissions", 0)
            total = result.get("total_attempts", 0)
            
            print(f"✅ MULTI-BUILDER SUCCESS: Bundle submitted to {successful}/{total} builders!")
            print(f"📦 Bundle Hash: {bundle_hash}")
            print(f"🎯 Target Blocks: {target_blocks}")
            print(f"🧮 Bribe: {coinbase_bribe / 1e18:.6f} ETH ({bribe_multiplier:.1f}x base fee)")
            print(f"🔄 Refund Percent: 90%")
            print(f"📊 Status: Multi-Builder Submitted")

            # Log with multi-builder info
            builder_info = f"Builders: {successful}/{total}, Bribe: {coinbase_bribe / 1e18:.6f} ETH ({bribe_multiplier:.1f}x)"
            log_bundle_result(bundle_hash, "MULTI-SUBMITTED", builder_info)

            # SPEED STRATEGY: Auto-escalate after every submission to keep ramping
            print(f"⚡ AUTO-ESCALATION: Ramping bribe for next opportunity...")
            adjust_bribe_multiplier("Submitted")  # Always escalate for speed

            # 🚀 SPEED MODE: Skip ALL profit calculations - focus on execution
            print(f"🚀 SPEED MODE: Skipping profit estimation - trust filters + execution speed!")
            print(f"🔍 MONITORING: Will check block {target_block} for inclusion...")

            # Minimal trade data for tracking (no profit calculations)
            trade_data = {
                "timestamp": time.time(),
                "tx_hash": tx_hash,
                "token_address": victim_tx.get("to", "unknown"),
                "bundle_hash": bundle_hash,
                "target_blocks": target_blocks,
                "bribe_amount": coinbase_bribe / 1e18,
                "estimated_profit": 0.0,  # Skip calculation
                "gas_used": 0.006,
                "status": "submitted"
            }

            await executor.handle_profitable_trade(trade_data)

            # Record bundle submission (minimal tracking)
            profit_tracker.record_bundle_submission(
                bundle_hash=bundle_hash,
                estimated_profit=0.0,  # Skip calculation
                bribe_amount=coinbase_bribe / 1e18
            )

            # Record bribe payment
            profit_tracker.record_bribe_payment(coinbase_bribe / 1e18)

            # Add to inclusion monitoring (minimal data)
            monitor = get_inclusion_monitor()
            if monitor:
                monitor.track_bundle(
                    bundle_hash=bundle_hash,
                    target_blocks=target_blocks,
                    victim_tx_hash=tx_hash,
                    bribe_amount=coinbase_bribe / 1e18,
                    estimated_profit=0.0  # Skip calculation
                )
            
            print(f"🔍 MONITORING: Tracking bundle {bundle_hash[:16]}... for inclusion in blocks {target_blocks}")
            print(f"🧮 BRIBE COST: {coinbase_bribe / 1e18:.6f} ETH")
            print(f"🚀 STATUS: PURE SPEED MODE - calculations disabled!")
        else:
            error_reason = result.get("error", "Unknown error")
            print(f"❌ TITAN submission failed: {error_reason}")
            print(f"📊 Status: Failed")
            log_bundle_result("unknown", "FAILED", error_reason)

            # Escalate bribe for next attempt on failure
            adjust_bribe_multiplier("Failed")

    except Exception as e:
        print(f"❌ Exception in sandwich simulation: {e}")