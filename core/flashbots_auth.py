
import os
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    # Create the raw keccak hash that Flashbots expects
    payload_hash = keccak(text=payload)
    
    # Sign the hash directly using the private key's sign method
    # This creates a raw ECDSA signature without message prefixes
    from eth_keys import keys
    private_key = keys.PrivateKey(SEARCHER_ACCOUNT.key)
    signature_obj = private_key.sign_msg_hash(payload_hash)
    
    # Convert to the hex format Flashbots expects
    signature = signature_obj.to_hex()
    
    return f"{SEARCHER_ACCOUNT.address}:{signature}"
