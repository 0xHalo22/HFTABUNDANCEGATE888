from core.flashbots import send_flashbots_bundle
from core.executor import Executor
from core.swap_builder import build_swap_tx
from web3 import Web3

executor = Executor()

async def simulate_sandwich_bundle(victim_tx, w3):
    print(f"💻 Handling tx: {victim_tx['hash'].hex()}")

    try:
        eth_to_send = w3.to_wei(0.001, "ether")

        # Guaranteed hex-formatted txs
        front_tx = build_swap_tx(w3, eth_to_send)
        back_tx = build_swap_tx(w3, eth_to_send)

        # Get victim tx raw hex
        victim_raw = w3.eth.get_raw_transaction(victim_tx["hash"]).hex()

        # Confirm all txs are strings
        print("📦 TX types:", type(front_tx), type(victim_raw), type(back_tx))

        bundle = [front_tx, victim_raw, back_tx]
        block_number = w3.eth.block_number + 1

        print("🧪 Flashbots bundle preview:", bundle)

        result = send_flashbots_bundle(bundle, block_number, w3)

        if not result.get("success"):
            print(f"❌ Bundle submission failed: {result}")
            return

        sim = result.get("response", {}).get("result", {})
        eth_sent = int(sim.get("eth_sent_to_coinbase", "0x0"), 16) if sim else 0
        profit = eth_sent / 1e18
        gas_cost = 0.0005
        net = profit - gas_cost

        print(f"📈 Live PnL: +{net:.5f} ETH (gross: {profit:.5f}, gas: {gas_cost:.5f})")

        tx_summary = {
            "token_address": victim_tx.get("to", "unknown"),
            "profit": round(net, 8),
            "gas_used": gas_cost,
            "status": "success"
        }

        await executor.handle_profitable_trade(tx_summary)

    except Exception as e:
        print(f"❌ Execution error: {e}")
