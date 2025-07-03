import os
import json
from web3 import Web3
from eth_account import Account

# Load private key & account
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = Account.from_key(PRIVATE_KEY)

# Uniswap V2 addresses
UNISWAP_ROUTER = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

def load_abi():
    with open("core/uniswap_v2_router_abi.json", "r") as f:
        return json.load(f)

def build_swap_tx(w3, eth_amount, nonce_offset=0, coinbase_bribe=0):
    """Build a swap transaction with proper nonce management and optional coinbase bribe"""

    # Get current nonce and add offset
    current_nonce = w3.eth.get_transaction_count(ACCOUNT.address, "pending")
    nonce = current_nonce + nonce_offset

    # Get current gas price and base fee
    gas_price = w3.eth.gas_price
    latest_block = w3.eth.get_block("latest")
    base_fee = latest_block.get("baseFeePerGas", gas_price)

    # ✅ Calculate competitive priority fee (25% above base fee for better inclusion)
    priority_fee = int(base_fee * 1.25)  # Increased from 20% to 25%
    print(f"⛽ Bidding {priority_fee / 1e9:.1f} gwei (25% above base)")

    # If coinbase bribe is specified, create a simple ETH transfer to coinbase
    if coinbase_bribe > 0:
        bribe_multiplier = coinbase_bribe / base_fee if base_fee > 0 else 2.0
        print(f"💸 Coinbase bribe: {coinbase_bribe / 1e18:.6f} ETH ({bribe_multiplier:.1f}x base fee)")

        # Get current coinbase address (validator)
        coinbase_address = latest_block["miner"]
        print(f"🎯 Validator: {coinbase_address}")

        # Create optimized ETH transfer transaction to coinbase
        tx = {
            "to": coinbase_address,
            "value": coinbase_bribe,
            "gas": 21000,  # Standard ETH transfer gas
            "gasPrice": priority_fee,  # Use same competitive gas price
            "nonce": nonce,
            "chainId": w3.eth.chain_id
        }

        # Sign the transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        hex_result = signed_tx.raw_transaction.hex()
        print(f"✅ [COINBASE BRIBE] Built: {hex_result[:12]}... (nonce: {nonce})")
        return hex_result

    router = w3.eth.contract(address=UNISWAP_ROUTER, abi=load_abi())

    path = [WETH_ADDRESS, DAI_ADDRESS]
    deadline = int(w3.eth.get_block("latest").timestamp + 120)

    # Estimate output tokens
    amounts_out = router.functions.getAmountsOut(eth_amount, path).call()
    min_out = int(amounts_out[1] * (1 - 0.01))

    # Build transaction with unique nonce
    base_nonce = w3.eth.get_transaction_count(ACCOUNT.address)
    # Bid 20% above current gas price for better inclusion
    base_gas_price = w3.eth.gas_price
    gas_price = int(base_gas_price * 1.2)
    print(f"⛽ Bidding {w3.from_wei(gas_price, 'gwei'):.1f} gwei (20% above base)")
    tx = router.functions.swapExactETHForTokens(
        min_out,
        path,
        ACCOUNT.address,
        deadline
    ).build_transaction({
        "from": ACCOUNT.address,
        "value": eth_amount,
        "gas": 250000,
        "gasPrice": gas_price,
        "nonce": base_nonce + nonce_offset,
        "chainId": w3.eth.chain_id
    })

    # Sign transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

    # 🧪 Debug the transaction object
    print("🚧 signed_tx type:", type(signed_tx))
    print("🚧 signed_tx dir:", dir(signed_tx))

    # ✅ Safe rawTransaction extraction with all fallback cases
    raw_tx = None
    if isinstance(signed_tx, dict):
        raw_tx = signed_tx.get("rawTransaction")
    elif hasattr(signed_tx, "rawTransaction"):
        raw_tx = signed_tx.rawTransaction
    elif hasattr(signed_tx, "raw_transaction"):  # ✅ this matches your actual case
        raw_tx = signed_tx.raw_transaction
    elif hasattr(signed_tx, "raw"):
        raw_tx = signed_tx.raw

    if raw_tx is None:
        raise ValueError("rawTransaction could not be extracted from signed transaction in build_swap_tx")

    hex_tx = Web3.to_hex(raw_tx)
    print("✅ [SWAP BUILDER] Returning hex:", hex_tx[:12], type(hex_tx))
    return hex_tx