from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak
import os

SEARCHER_KEY = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(SEARCHER_KEY)

def sign_flashbots_payload(payload: str):
    # Compute keccak256 of the payload
    hashed = keccak(text=payload)

    # Create a defunct message from the raw hash bytes
    message = encode_defunct(primitive=hashed)

    # Sign with searcher's account
    signed = SEARCHER_ACCOUNT.sign_message(message)

    # Return the Flashbots-required header format
    return f"{SEARCHER_ACCOUNT.address}:{signed.signature.hex()}"
