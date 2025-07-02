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
    return signed.rawTransaction.hex()

def get_address():
    return ACCOUNT.address
