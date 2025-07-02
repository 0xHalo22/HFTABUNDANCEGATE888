
import os
from eth_account import Account
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    # Create the raw keccak hash that Flashbots expects
    payload_hash = keccak(text=payload)
    
    # Sign the hash directly using the private key
    signed = SEARCHER_ACCOUNT._key_obj.sign_msg_hash(payload_hash)
    
    # Convert to hex signature
    signature = signed.to_hex()
    
    return f"{SEARCHER_ACCOUNT.address}:{signature}"
