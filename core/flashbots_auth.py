from eth_account import Account
from eth_account.messages import encode_defunct
import os

SEARCHER_KEY = os.getenv("PRIVATE_KEY_SEARCHER")
if SEARCHER_KEY.startswith("0x"):
    SEARCHER_KEY = SEARCHER_KEY[2:]

SEARCHER_ACCOUNT = Account.from_key(SEARCHER_KEY)

def sign_flashbots_payload(payload: str):
    # Assume payload is already canonicalized
    message = encode_defunct(text=payload)
    signed = SEARCHER_ACCOUNT.sign_message(message)
    return f"{SEARCHER_ACCOUNT.address}:{signed.signature.hex()}"
