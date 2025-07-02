
import os
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    # Create the raw keccak hash that Flashbots expects
    payload_hash = keccak(text=payload)
    
    # Convert hash to signable message format
    message = encode_defunct(payload_hash)
    
    # Sign the message
    signed = SEARCHER_ACCOUNT.sign_message(message)
    
    # Convert to hex signature
    signature = signed.signature.hex()
    
    return f"{SEARCHER_ACCOUNT.address}:{signature}"
