
import os
from eth_account import Account
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    # Create the raw keccak hash that Flashbots expects
    payload_hash = keccak(text=payload)
    
    # Sign the hash directly using eth_account's signHash method
    # This creates the raw ECDSA signature that Flashbots expects
    signed = SEARCHER_ACCOUNT.signHash(payload_hash)
    
    # Convert to hex signature
    signature = signed.signature.hex()
    
    return f"{SEARCHER_ACCOUNT.address}:{signature}"
