
import os
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    # Create the raw keccak hash that Flashbots expects
    payload_hash = keccak(text=payload)
    
    # Use eth_account's built-in unsafe_hash signing 
    # This signs the raw hash without any message prefix
    signed = SEARCHER_ACCOUNT.unsafe_hash_and_sign(payload_hash)
    
    # Convert to hex signature
    signature = signed.signature.hex()
    
    return f"{SEARCHER_ACCOUNT.address}:{signature}"
