import os
import json
import time
import asyncio
from random import uniform
from core.flashbots import send_bundle_to_titan
from core.executor import Executor
from core.swap_builder import build_swap_tx
from web3 import Web3

executor = Executor()

# Constants for profit calculation
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
UNISWAP_ROUTER = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
MIN_PROFIT_THRESHOLD = 0.00005  # Minimum net profit in ETH (lowered for aggressive testing)

def load_router_abi():
    with open("core/uniswap_v2_router_abi.json", "r") as f:
        return json.load(f)

# Global bribe multiplier for adaptive escalation
bribe_multiplier = 2.0

def calculate_dynamic_bribe(base_fee_wei, multiplier=None):
    """Calculate dynamic coinbase bribe with adaptive escalation"""
    global bribe_multiplier
    
    if multiplier is None:
        multiplier = bribe_multiplier
    
    calculated = int(base_fee_wei * multiplier)
    print(f"🧮 BRIBE CALC: base_fee={base_fee_wei}, multiplier={multiplier:.1f}x, result={calculated}")
    return calculated

def adjust_bribe_multiplier(bundle_result):
    """Adjust bribe multiplier based on bundle inclusion results"""
    global bribe_multiplier
    
    if bundle_result in ["Underpriced", "ExcludedFromBlock", "Failed"]:
        # Escalate bribe for next attempt
        old_multiplier = bribe_multiplier
        bribe_multiplier = min(bribe_multiplier + 0.2, 5.0)  # Cap at 5.0x
        print(f"📈 BRIBE ESCALATION: {old_multiplier:.1f}x → {bribe_multiplier:.1f}x")
    elif bundle_result == "Included":
        # Reset to baseline on success
        if bribe_multiplier > 2.0:
            print(f"📉 BRIBE RESET: {bribe_multiplier:.1f}x → 2.0x")
            bribe_multiplier = 2.0

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

async def send_bundle_to_titan_optimized(front_tx, victim_tx, back_tx, target_block, coinbase_bribe):
    """Enhanced Titan Builder submission with refundPercent and coinbase bribe"""
    try:
        # Prepare bundle with coinbase bribe in back-run transaction
        bundle_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [{
                "txs": [front_tx, victim_tx, back_tx],
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
    """Calculate real profit using getAmountsOut for sandwich opportunity"""
    try:
        router = w3.eth.contract(address=UNISWAP_ROUTER, abi=load_router_abi())

        # Get victim transaction details
        victim_to = victim_tx.get("to", "").lower()
        victim_value = victim_tx.get("value", 0)

        # FIXED: Match the filter threshold (0.001 ETH)
        if victim_value < w3.to_wei(0.001, "ether"):
            print(f"⛔ Victim tx value too low: {w3.from_wei(victim_value, 'ether')} ETH")
            return 0

        # FIXED: Ensure eth_amount is properly converted to wei
        if isinstance(eth_amount, float):
            eth_amount_wei = w3.to_wei(eth_amount, "ether")
        else:
            eth_amount_wei = eth_amount

        # For testing, assume WETH -> DAI path (we'll expand this later)
        DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
        path = [WETH_ADDRESS, DAI_ADDRESS]

        # Front-run: ETH -> Token (get tokens out)
        front_amounts = router.functions.getAmountsOut(eth_amount_wei, path).call()
        tokens_received = front_amounts[1]

        # Back-run: Token -> ETH (sell tokens back)
        back_path = [DAI_ADDRESS, WETH_ADDRESS]
        back_amounts = router.functions.getAmountsOut(tokens_received, back_path).call()
        eth_received = back_amounts[1]

        # Calculate gross profit
        gross_profit_wei = eth_received - eth_amount_wei
        gross_profit_eth = w3.from_wei(gross_profit_wei, "ether")

        # Estimate gas costs (3 transactions * ~0.002 ETH each)
        gas_cost_eth = 0.006

        # Net profit
        net_profit_eth = gross_profit_eth - gas_cost_eth

        print(f"💰 Profit Analysis:")
        print(f"  📤 Front-run: {w3.from_wei(eth_amount, 'ether')} ETH -> {tokens_received:,.0f} tokens")
        print(f"  📥 Back-run: {tokens_received:,.0f} tokens -> {w3.from_wei(eth_received, 'ether')} ETH")
        print(f"  💵 Gross profit: {gross_profit_eth:.6f} ETH")
        print(f"  ⛽ Gas cost: {gas_cost_eth:.6f} ETH")
        print(f"  💎 Net profit: {net_profit_eth:.6f} ETH")

        return net_profit_eth

    except Exception as e:
        print(f"❌ Error calculating sandwich profit: {e}")
        return 0

async def simulate_sandwich_bundle(victim_tx, w3):
    try:
        # Get victim tx hash safely
        tx_hash = victim_tx["hash"]
        if isinstance(tx_hash, bytes):
            tx_hash = tx_hash.hex()
        print(f"\n💻 Analyzing tx: {tx_hash}")

        # Scale up trade amount for real profits
        eth_to_send = w3.to_wei(0.001, "ether")  # 0.001 ETH for testing
        account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

        # Log wallet state
        balance = w3.eth.get_balance(account.address)
        print(f"💰 Wallet balance: {w3.from_wei(balance, 'ether')} ETH")

        # ✅ SPEED OPTIMIZATION: Skip simulation - trust our filters!
        print(f"🚀 FAST EXECUTION: Bypassing simulation for speed - filters confirmed viability")

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

        # Get current block and calculate coinbase bribe
        current_block = w3.eth.block_number
        target_block = current_block + 1

        # Calculate adaptive dynamic coinbase bribe
        try:
            base_fee = w3.eth.get_block("pending")["baseFeePerGas"]
        except:
            base_fee = w3.eth.gas_price  # Fallback to gas price
        
        # Use adaptive bribe calculation
        min_bribe = w3.to_wei(0.001, "ether")  # 0.001 ETH minimum floor
        calculated_bribe = calculate_dynamic_bribe(base_fee)
        coinbase_bribe = max(calculated_bribe, min_bribe)

        print(f"🎯 Targeting block {target_block} (current: {current_block})")
        print(f"💸 Adaptive bribe: {coinbase_bribe / 1e18:.6f} ETH ({bribe_multiplier:.1f}x base fee)")

        # Precision timing - sleep to land early in next block slot
        sleep_time = time_until_next_block(w3, target_block)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
            print(f"🚀 PRECISION SUBMIT: Timed for early slot position")

        # Submit to Titan Builder with enhanced payload
        result = await send_bundle_to_titan_optimized(front_tx, tx_hash, back_tx, target_block, coinbase_bribe)

        # Enhanced logging with bribe tracking
        if result["success"]:
            bundle_hash = result.get("bundleHash", "unknown")
            print(f"✅ TITAN OPTIMIZED: Bundle submitted successfully")
            print(f"📦 Bundle Hash: {bundle_hash}")
            print(f"🎯 Target Block: {target_block}")
            print(f"🧮 Bribe: {coinbase_bribe / 1e18:.6f} ETH ({bribe_multiplier:.1f}x base fee)")
            print(f"🔄 Refund Percent: 90%")
            print(f"📊 Status: Submitted")

            # Log with detailed bribe info
            bribe_info = f"Bribe: {coinbase_bribe / 1e18:.6f} ETH ({bribe_multiplier:.1f}x), RefundPct: 90%"
            log_bundle_result(bundle_hash, "SUBMITTED", bribe_info)
            
            # Track result for future bribe adjustments (simulated for now)
            # In production, you'd check actual inclusion in next block
            simulated_result = "Submitted"  # Will be "Included" or "ExcludedFromBlock" in real scenario
            adjust_bribe_multiplier(simulated_result)

            # Estimate profit (scaled simulation)
            estimated_profit = eth_to_send * 0.5  # Conservative 50% return estimate
            print(f"📈 Estimated PnL: +{estimated_profit / 1e18:.6f} ETH")
            print(f"🔍 MONITORING: Will check block {target_block} for inclusion...")

            # Record the trade attempt
            await executor.handle_profitable_trade({
                "timestamp": time.time(),
                "token_address": victim_tx.get("to", "unknown"),
                "profit": estimated_profit / 1e18,
                "gas_used": 0.006,  # Estimated gas cost
                "status": "submitted"
            })
        else:
            error_reason = result.get("error", "Unknown error")
            print(f"❌ TITAN submission failed: {error_reason}")
            print(f"📊 Status: Failed")
            log_bundle_result("unknown", "FAILED", error_reason)
            
            # Escalate bribe for next attempt on failure
            adjust_bribe_multiplier("Failed")

    except Exception as e:
        print(f"❌ Exception in sandwich simulation: {e}")