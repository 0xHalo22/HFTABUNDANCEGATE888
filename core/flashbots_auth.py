
import os
import json
from eth_account import Account
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    # Canonical Flashbots expects raw keccak hash signature
    payload_hash = keccak(text=payload)  # 👈 no prefixing
    signed = SEARCHER_ACCOUNT.signHash(payload_hash)
    return f"{SEARCHER_ACCOUNT.address}:{signed.signature.hex()}"
