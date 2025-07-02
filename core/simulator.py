import os
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
        account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

        # Log wallet state
        balance = w3.eth.get_balance(account.address)
        print(f"💰 Wallet balance: {w3.from_wei(balance, 'ether')} ETH")

        # Build front-run and back-run txs with different nonces (must return hex)
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

        # Victim tx hash
        print("↪ victim_tx hash:", tx_hash)

        # Build Flashbots bundle
        bundle = [front_tx, tx_hash, back_tx]
        block_number = w3.eth.block_number + 1

        print(f"🧪 Flashbots bundle → block {block_number}:")
        for i, tx in enumerate(bundle):
            print(f"  🔗 tx[{i}]:", tx[:24], "...")

        # Submit bundle
        result = send_flashbots_bundle(bundle, block_number, w3)

        if not result.get("success"):
            print(f"❌ Bundle submission failed:\n{result}")
            return

        # Simulated result parse
        sim = result.get("response", {}).get("result", {})
        eth_sent = int(sim.get("eth_sent_to_coinbase", "0x0"), 16) if sim else 0
        profit = eth_sent / 1e18
        gas_cost = 0.0005
        net = profit - gas_cost

        print(f"📈 Live PnL: +{net:.5f} ETH (gross: {profit:.5f}, gas: {gas_cost:.5f})")

        # Record trade
        tx_summary = {
            "token_address": victim_tx.get("to", "unknown"),
            "profit": round(net, 8),
            "gas_used": gas_cost,
            "status": "success"
        }

        await executor.handle_profitable_trade(tx_summary)

    except Exception as e:
        print(f"❌ Execution error on tx {tx_hash}: {e}")


