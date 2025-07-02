import os
from core.flashbots import simulate_bundle
from core.signer import build_signed_tx, get_address
from core.executor import send_bundle

MODE = os.getenv("MODE", "sim")

def simulate_sandwich_bundle(victim_tx, w3):
    print(f"💻 Handling tx: {victim_tx['hash'].hex()}")

    try:
        victim_raw = w3.eth.get_raw_transaction(victim_tx["hash"]).hex()
    except Exception as e:
        print(f"❌ Error fetching raw tx: {e}")
        return

    try:
        eth_to_send = w3.to_wei(0.001, "ether")
        front_tx = build_signed_tx(w3, get_address(), eth_to_send)
        back_tx = build_signed_tx(w3, get_address(), eth_to_send)

        if MODE == "live":
            send_bundle(front_tx, victim_raw, back_tx, w3)
        else:
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
            with open("data/trade_log.csv", "a") as log:
                log.write(f"{victim_tx['hash'].hex()},{profit},{gas_cost},{net}\n")
            print(f"🧪 Logged to file: {victim_tx['hash'].hex()}")
    except Exception as e:
        print(f"❌ Bundle build/sim error: {e}")
