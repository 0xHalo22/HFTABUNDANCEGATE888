import os
from eth_account.account import Account, LocalAccount
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT: LocalAccount = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    payload_hash = keccak(text=payload)
    signed = SEARCHER_ACCOUNT.signHash(payload_hash)
    return f"{SEARCHER_ACCOUNT.address}:{signed.signature.hex()}"
