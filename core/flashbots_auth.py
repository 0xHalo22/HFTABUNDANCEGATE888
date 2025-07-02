
import os
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    # Create the raw keccak hash that Flashbots expects
    payload_hash = keccak(text=payload)
    
    # Sign the raw hash directly without any message prefix
    # Flashbots expects a pure ECDSA signature of the keccak hash
    signed = SEARCHER_ACCOUNT._private_key.sign_digest_deterministic(payload_hash)
    
    # Convert to hex signature  
    signature = signed.to_hex()
    
    return f"{SEARCHER_ACCOUNT.address}:{signature}"
