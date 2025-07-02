
import os
import json
from eth_account import Account
from eth_account.messages import encode_defunct

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str):
    # This signs the canonical JSON string Flashbots expects
    message = encode_defunct(text=payload)
    signed = SEARCHER_ACCOUNT.sign_message(message)
    signature = signed.signature.hex()
    return f"{SEARCHER_ACCOUNT.address}:{signature}"
