
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
    
    # Build 64-byte signature from r,s components (without recovery ID)
    r_hex = format(signed.r, '064x')  # 32 bytes (64 hex chars)
    s_hex = format(signed.s, '064x')  # 32 bytes (64 hex chars)
    signature_64_bytes = r_hex + s_hex  # Total: 64 bytes (128 hex chars)
    
    print(f"🔬 Signature debug:")
    print(f"  - r: {r_hex}")
    print(f"  - s: {s_hex}")
    print(f"  - 64-byte signature: {signature_64_bytes}")
    print(f"  - Length: {len(signature_64_bytes)} chars")
    
    return f"{SEARCHER_ACCOUNT.address}:0x{signature_64_bytes}"
