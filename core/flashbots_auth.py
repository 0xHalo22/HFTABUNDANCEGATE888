from eth_account import Account
from web3 import Web3
import os

SEARCHER_KEY = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(SEARCHER_KEY)

def sign_flashbots_payload(payload: str):
    # Compute keccak256 of the payload
    hashed = Web3.keccak(text=payload)

    # Sign the raw hash directly (no Ethereum message prefix)
    signed = SEARCHER_ACCOUNT.sign_hash(hashed)

    # Return the Flashbots-required header format
    return f"{SEARCHER_ACCOUNT.address}:{signed.signature.hex()}"
