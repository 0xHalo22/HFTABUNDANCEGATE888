import os
from web3 import Web3
from eth_account import Account
import json

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = Account.from_key(PRIVATE_KEY)

UNISWAP_ROUTER = "0xf164fC0Ec4E93095b804a4795bBe1e041497b92a"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
DAI_ADDRESS = "0x6B175474E89094C44Da98b954EedeAC495271d0F"

def load_abi():
    with open("core/uniswap_v2_router_abi.json", "r") as f:
        return json.load(f)

def build_swap_tx(w3, amount_in_wei, slippage_tolerance=0.01):
    router = w3.eth.contract(address=UNISWAP_ROUTER, abi=load_abi())

    path = [WETH_ADDRESS, DAI_ADDRESS]
    deadline = int(w3.eth.get_block("latest").timestamp + 120)

    amounts_out = router.functions.getAmountsOut(amount_in_wei, path).call()
    min_out = int(amounts_out[1] * (1 - slippage_tolerance))

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
        "nonce": w3.eth.get_transaction_count(ACCOUNT.address),
        "chainId": w3.eth.chain_id
    })

    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    return Web3.to_hex(signed.rawTransaction)  # 🔥 This ensures string output
