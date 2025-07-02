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

def build_swap_tx(w3, amount_in_wei, slippage_tolerance=0.01, nonce_offset=0):
    router = w3.eth.contract(address=UNISWAP_ROUTER, abi=load_abi())

    path = [WETH_ADDRESS, DAI_ADDRESS]
    deadline = int(w3.eth.get_block("latest").timestamp + 120)

    # Estimate output tokens
    amounts_out = router.functions.getAmountsOut(amount_in_wei, path).call()
    min_out = int(amounts_out[1] * (1 - slippage_tolerance))

    # Build transaction with unique nonce
    base_nonce = w3.eth.get_transaction_count(ACCOUNT.address)
    tx = router.functions.swapExactETHForTokens(
        min_out,
        path,
        ACCOUNT.address,
        deadline
    ).build_transaction({
        "from": ACCOUNT.address,
        "value": amount_in_wei,
        "gas": 250000,
        "gasPrice": w3.eth.gas_price,
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
