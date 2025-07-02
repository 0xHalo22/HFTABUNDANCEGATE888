
import os
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    # Create the raw keccak hash that Flashbots expects
    payload_hash = keccak(text=payload)
    
    # Convert HexBytes to raw bytes for signing
    hash_bytes = bytes(payload_hash)
    
    # Sign the raw hash directly using the private key
    # Flashbots expects a pure ECDSA signature of the keccak hash
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    
    # Get the private key in the right format
    private_key_int = int(SEARCHER_ACCOUNT.key.hex(), 16)
    private_key_obj = ec.derive_private_key(private_key_int, ec.SECP256K1())
    
    # Sign the hash
    signature = private_key_obj.sign(hash_bytes, ec.ECDSA(hashes.SHA256()))
    
    # Convert to hex format that Flashbots expects
    signature_hex = signature.hex()
    
    return f"{SEARCHER_ACCOUNT.address}:{signature_hex}"
