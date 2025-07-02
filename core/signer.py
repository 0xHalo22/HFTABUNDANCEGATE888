import os
from web3 import Web3
from eth_account import Account

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = Account.from_key(PRIVATE_KEY)

def build_signed_tx(w3, to_address, value_wei, gas=21000, gas_price_wei=None):
    nonce = w3.eth.get_transaction_count(ACCOUNT.address)
    if gas_price_wei is None:
        gas_price_wei = w3.eth.gas_price

    tx = {
        "to": to_address,
        "value": value_wei,
        "gas": gas,
        "gasPrice": gas_price_wei,
        "nonce": nonce,
        "chainId": w3.eth.chain_id
    }

    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

    print("🚧 DEBUG: signed type =", type(signed))
    print("🚧 DEBUG: signed keys/attrs =", dir(signed))


    # ✅ Fully defensive handling of SignedTransaction or dict
    if isinstance(signed, dict):
        raw_tx = signed.get("rawTransaction")
    else:
        raw_tx = getattr(signed, "rawTransaction", None)

    if raw_tx is None:
        raise ValueError("rawTransaction could not be extracted from signed transaction.")

    return Web3.to_hex(raw_tx)

def get_address():
    return ACCOUNT.address
