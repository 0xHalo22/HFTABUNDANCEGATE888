from eth_account import Account
from eth_account.messages import encode_defunct
import os
import json

SEARCHER_KEY = os.getenv("PRIVATE_KEY_SEARCHER")
if SEARCHER_KEY.startswith("0x"):
    SEARCHER_KEY = SEARCHER_KEY[2:]

SEARCHER_ACCOUNT = Account.from_key(SEARCHER_KEY)

def sign_flashbots_payload(payload: str) -> str:
    # Canonicalize payload before signing
    compact_payload = json.dumps(json.loads(payload), separators=(",", ":"))
    message = encode_defunct(text=compact_payload)
    signed = SEARCHER_ACCOUNT.sign_message(message)
    return f"{SEARCHER_ACCOUNT.address}:{signed.signature.hex()}"
