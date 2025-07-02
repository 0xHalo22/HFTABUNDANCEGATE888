
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
    
    # Try approach 1: 64-byte signature without 0x prefix
    r_hex = format(signed.r, '064x')
    s_hex = format(signed.s, '064x') 
    signature_64_no_prefix = r_hex + s_hex
    
    # Try approach 2: Original 65-byte signature without 0x prefix
    original_sig = signed.signature.hex()
    signature_65_no_prefix = original_sig[2:] if original_sig.startswith('0x') else original_sig
    
    print(f"🔬 Testing signature formats:")
    print(f"  - 64-byte (no 0x): {signature_64_no_prefix}")
    print(f"  - 65-byte (no 0x): {signature_65_no_prefix}")
    
    # Use 64-byte without 0x prefix (most common format)
    return f"{SEARCHER_ACCOUNT.address}:{signature_64_no_prefix}"
