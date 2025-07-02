import os
from core.flashbots import simulate_bundle
from core.signer import build_signed_tx, get_address
from core.executor import Executor

# Set mode to "sim" or "live" via env
MODE = os.getenv("MODE", "sim")

# Create executor instance
executor = Executor()

async def simulate_sandwich_bundle(victim_tx, w3):
    print(f"💻 Handling tx: {victim_tx['hash'].hex()}")

    try:
        victim_raw = w3.eth.get_raw_transaction(victim_tx["hash"]).hex()
    except Exception as e:
        print(f"❌ Error fetching raw tx: {e}")
        return

    try:
        # Create front and back tx
        eth_to_send = w3.to_wei(0.001, "ether")
        front_tx = build_signed_tx(w3, get_address(), eth_to_send)
        back_tx = build_signed_tx(w3, get_address(), eth_to_send)

        if MODE == "live":
            print("🚨 LIVE MODE ENABLED — but send_bundle() is not implemented.")
            return  # Skip for now

        # Simulate bundle in SIM mode
        bundle = [front_tx, victim_raw, back_tx]
        block_number = w3.eth.block_number + 1
        result = simulate_bundle(bundle, block_number)

        if "error" in result:
            print(f"❌ Simulation error: {result['error']}")
            return

        print(f"📬 Flashbots response: {result}")
        profit = int(result.get('eth_sent_to_coinbase', '0x0'), 16) / 1e18
        gas_cost = 0.0005
        net = profit - gas_cost

        print(f"📈 Flashbots Sim PnL: +{net:.5f} ETH (gross: {profit:.5f}, gas: {gas_cost:.5f})")

        # Send trade summary to executor
        tx_summary = {
            "token_address": victim_tx["to"],
            "profit": round(net, 8),
            "gas_used": gas_cost,
            "status": "success"
        }

        await executor.handle_profitable_trade(tx_summary)

    except Exception as e:
        print(f"❌ Bundle build/sim error: {e}")
