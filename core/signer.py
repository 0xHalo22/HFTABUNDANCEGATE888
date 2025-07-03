import os
from web3 import Web3
from eth_account import Account

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = Account.from_key(PRIVATE_KEY)

def build_signed_tx(w3, to_address, value_wei, gas=21000, gas_price_wei=None):
    nonce = w3.eth.get_transaction_count(ACCOUNT.address)
    if gas_price_wei is None:
        gas_price_wei = w3.eth.gas_price

    # Use EIP-1559 for better inclusion probability
    latest_block = w3.eth.get_block('latest')
    base_fee = latest_block.baseFeePerGas
    
    tx = {
        "to": to_address,
        "value": value_wei,
        "gas": gas,
        "maxFeePerGas": base_fee * 2,  # 2x base fee
        "maxPriorityFeePerGas": w3.to_wei(2, 'gwei'),  # 2 gwei tip
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
        "type": 2  # EIP-1559 transaction
    }
    
    print(f"💰 EIP-1559: MaxFee={w3.from_wei(tx['maxFeePerGas'], 'gwei'):.1f} gwei, Tip=2 gwei")

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
