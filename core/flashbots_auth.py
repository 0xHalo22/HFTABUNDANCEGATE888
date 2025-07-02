
import os
from eth_account.signers.local import LocalAccount
from eth_account import Account
from eth_account.messages import encode_defunct

PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
assert PRIVATE_KEY_SEARCHER, "Missing PRIVATE_KEY_SEARCHER in env"

# Create signer
SEARCHER_ACCOUNT: LocalAccount = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    message = encode_defunct(text=payload)
    signed = SEARCHER_ACCOUNT.sign_message(message)
    
    # DEBUG: Print all signature components
    print(f"🔬 Signature debug:")
    print(f"  - signed type: {type(signed)}")
    print(f"  - signed dir: {[attr for attr in dir(signed) if not attr.startswith('_')]}")
    print(f"  - signature: {signed.signature.hex()}")
    print(f"  - v: {signed.v}")
    print(f"  - r: {signed.r}")
    print(f"  - s: {signed.s}")
    
    # Try the standard format (what we've been using)
    signature_hex = signed.signature.hex()
    
    # Alternative: try without 0x prefix
    signature_no_prefix = signature_hex[2:] if signature_hex.startswith('0x') else signature_hex
    
    print(f"  - signature with 0x: {signature_hex}")
    print(f"  - signature without 0x: {signature_no_prefix}")
    
    return f"{SEARCHER_ACCOUNT.address}:{signature_hex}"
