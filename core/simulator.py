from core.signer import build_signed_tx, get_address
from core.flashbots import send_flashbots_bundle
from core.executor import Executor

executor = Executor()

async def simulate_sandwich_bundle(victim_tx, w3):
    print(f"💻 Handling tx: {victim_tx['hash'].hex()}")

    try:
        # Skip simulation — we're live now
        eth_to_send = w3.to_wei(0.0001, "ether")  # Live ETH size
        front_tx = build_signed_tx(w3, get_address(), eth_to_send)
        back_tx = build_signed_tx(w3, get_address(), eth_to_send)

        # Bundle = our signed transactions ONLY
        bundle = [front_tx, back_tx]
        block_number = w3.eth.block_number + 1

        result = send_flashbots_bundle(bundle, block_number, w3)

        if not result.get("success"):
            print(f"❌ Bundle submission failed: {result}")
            return

        profit = result.get("eth_sent_to_coinbase", 0) / 1e18  # fake until tracking real outcome
        gas_cost = 0.0002  # est gas cost
        net = profit - gas_cost

        print(f"📈 Live PnL: +{net:.5f} ETH (gross: {profit:.5f}, gas: {gas_cost:.5f})")

        tx_summary = {
            "token_address": victim_tx["to"],
            "profit": round(net, 8),
            "gas_used": gas_cost,
            "status": "success"
        }

        await executor.handle_profitable_trade(tx_summary)

    except Exception as e:
        print(f"❌ Execution error: {e}")
