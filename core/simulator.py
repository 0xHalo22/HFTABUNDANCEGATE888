
import os
from core.flashbots import send_bundle_to_titan
from core.executor import Executor
from core.swap_builder import build_swap_tx
from web3 import Web3

executor = Executor()

async def simulate_sandwich_bundle(victim_tx, w3):
    try:
        # Get victim tx hash safely
        tx_hash = victim_tx["hash"]
        if isinstance(tx_hash, bytes):
            tx_hash = tx_hash.hex()
        print(f"\n💻 Handling tx: {tx_hash}")

        eth_to_send = w3.to_wei(0.001, "ether")
        account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

        # Log wallet state
        balance = w3.eth.get_balance(account.address)
        print(f"💰 Wallet balance: {w3.from_wei(balance, 'ether')} ETH")

        # Build front-run and back-run txs with different nonces
        front_tx = build_swap_tx(w3, eth_to_send, nonce_offset=0)
        back_tx = build_swap_tx(w3, eth_to_send, nonce_offset=2)

        print("✅ TX FORMAT CHECK")
        print("↪ front_tx:", front_tx[:12], type(front_tx))
        print("↪ back_tx :", back_tx[:12], type(back_tx))
        print("🧬 TXs identical?", front_tx == back_tx)

        # Sanity check
        if not all(isinstance(tx, str) for tx in [front_tx, back_tx]):
            print("❌ One or more txs are not hex strings!")
            return

        # Target next block
        current_block = w3.eth.block_number
        target_block = current_block + 1

        print(f"🎯 Targeting block {target_block} (current: {current_block})")

        # Submit bundle to Titan
        result = send_bundle_to_titan(front_tx, tx_hash, back_tx, target_block)

        if not result.get("success"):
            print(f"❌ Titan bundle submission failed:\n{result}")
            return

        # Simulated profit calculation
        gas_cost = 0.0005
        estimated_profit = 0.001  # Simplified for now
        net_profit = estimated_profit - gas_cost

        print(f"📈 Estimated PnL: +{net_profit:.5f} ETH (gross: {estimated_profit:.5f}, gas: {gas_cost:.5f})")

        # Record trade
        tx_summary = {
            "token_address": victim_tx.get("to", "unknown"),
            "profit": round(net_profit, 8),
            "gas_used": gas_cost,
            "status": "submitted"
        }

        await executor.handle_profitable_trade(tx_summary)

    except Exception as e:
        print(f"❌ Exception in sandwich simulation: {e}")
