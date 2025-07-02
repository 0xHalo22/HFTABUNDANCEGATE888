
import os
import json
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

# Load private key from environment
PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
assert PRIVATE_KEY_SEARCHER, "Missing PRIVATE_KEY_SEARCHER in env"

# Create signer account
SEARCHER_ACCOUNT = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload_dict: dict) -> tuple[str, str]:
    """
    Signs the payload dict for Flashbots using the verified method.
    
    Args:
        payload_dict (dict): The payload dictionary to sign

    Returns:
        tuple: (header_value, canonical_json) for use in requests
    """
    print("🔄 [SIGNATURE] Starting Flashbots signature process...")
    
    # Step 1: Canonicalize JSON payload
    canonical_json = json.dumps(payload_dict, separators=(",", ":"), sort_keys=True)
    
    # Step 2: keccak256 hash of UTF-8 encoded JSON string  
    digest = Web3.keccak(canonical_json.encode("utf-8"))
    
    # Step 3: Use EIP-191 signing with digest directly (critical fix!)
    message = encode_defunct(digest)
    signed = SEARCHER_ACCOUNT.sign_message(message)
    signature_hex = signed.signature.hex()
    
    # Step 4: Construct header
    header_value = f"{SEARCHER_ACCOUNT.address}:{signature_hex}"
    
    print("🧾 Canonical JSON:", canonical_json)
    print("🔑 Digest:", digest.hex())
    print("📦 EIP-191 Message:", message)
    print("✍️ Signature:", signature_hex)
    print("🔐 Header:", header_value)
    
    return header_value, canonical_json
