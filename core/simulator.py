from core.flashbots import send_flashbots_bundle
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

        # Build front-run and back-run txs (must return hex)
        front_tx = build_swap_tx(w3, eth_to_send)
        back_tx = build_swap_tx(w3, eth_to_send)

        print("✅ TX FORMAT CHECK")
        print("↪ front_tx:", front_tx[:12], type(front_tx))
        print("↪ back_tx :", back_tx[:12], type(back_tx))

        # Sanity check
        if not all(isinstance(tx, str) for tx in [front_tx, back_tx]):
            print("❌ One or more txs are not hex strings!")
            return

        # Use victim tx hash directly (Flashbots will resolve it)
        print("↪ victim_tx hash:", tx_hash)

        # Create Flashbots bundle
        bundle = [front_tx, tx_hash, back_tx]
        block_number = w3.eth.block_number + 1

        print(f"🧪 Flashbots bundle → block {block_number}:")
        print(bundle)

        result = send_flashbots_bundle(bundle, block_number, w3)

        if not result.get("success"):
            print(f"❌ Bundle submission failed:\n{result}")
            return

        # Parse simulated result
        sim = result.get("response", {}).get("result", {})
        eth_sent = int(sim.get("eth_sent_to_coinbase", "0x0"), 16) if sim else 0
        profit = eth_sent / 1e18
        gas_cost = 0.0005  # Update this if you're using real gas tracking
        net = profit - gas_cost

        print(f"📈 Live PnL: +{net:.5f} ETH (gross: {profit:.5f}, gas: {gas_cost:.5f})")

        # Record trade summary
        tx_summary = {
            "token_address": victim_tx.get("to", "unknown"),
            "profit": round(net, 8),
            "gas_used": gas_cost,
            "status": "success"
        }

        await executor.handle_profitable_trade(tx_summary)

    except Exception as e:
        print(f"❌ Execution error on tx {tx_hash}: {e}")
