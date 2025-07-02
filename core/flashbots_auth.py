
import os
import json
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_defunct
from web3 import Web3

# Load private key from environment
PRIVATE_KEY_SEARCHER = os.getenv("PRIVATE_KEY_SEARCHER")
assert PRIVATE_KEY_SEARCHER, "Missing PRIVATE_KEY_SEARCHER in env"

# Create signer account
SEARCHER_ACCOUNT: LocalAccount = Account.from_key(PRIVATE_KEY_SEARCHER)

def sign_flashbots_payload(payload: str) -> str:
    """
    Signs the canonical JSON payload for Flashbots.
    Based on Flashbots docs, trying direct keccak256 signing.
    
    Args:
        payload (str): Canonical JSON string (e.g., json.dumps(..., separators=(",", ":"), sort_keys=True))

    Returns:
        str: X-Flashbots-Signature header value in format "0xAddress:0xSignature"
    """
    print("🔄 [SIGNATURE] Starting Flashbots signature process...")
    
    # Step 1: keccak256 hash of UTF-8 encoded JSON string
    digest = Web3.keccak(payload.encode("utf-8"))
    print("🧾 Canonical JSON Payload:\n", payload)
    print("🔑 Keccak256 Digest:", digest.hex())

    # TRY APPROACH 1: Direct signing of keccak256 hash (no EIP-191)
    try:
        # Get raw private key bytes and sign directly
        private_key_bytes = SEARCHER_ACCOUNT._key_obj
        signature = private_key_bytes.sign_msg_hash(digest)
        
        # Convert to 65-byte format: r (32) + s (32) + v (1)
        signature_hex = '0x' + signature.to_bytes().hex()
        
        print("✍️ Direct Signature (65-byte):", signature_hex)
        print("🔐 Signer Address:", SEARCHER_ACCOUNT.address)

        # Step 4: Construct X-Flashbots-Signature header
        header_value = f"{SEARCHER_ACCOUNT.address}:{signature_hex}"
        print("✅ Final Header (X-Flashbots-Signature):", header_value)

        return header_value
        
    except Exception as e:
        print(f"❌ Direct signing failed: {e}")
        
        # FALLBACK: EIP-191 method (our current approach)
        print("🔄 Falling back to EIP-191 method...")
        message = encode_defunct(hexstr=digest.hex())
        print("📦 EIP-191 Encoded Message:\n", message)

        signed = SEARCHER_ACCOUNT.sign_message(message)
        signature_hex = signed.signature.hex()

        print("✍️ EIP-191 Signature (65-byte):", signature_hex)
        print("🔐 Signer Address:", SEARCHER_ACCOUNT.address)

        header_value = f"{SEARCHER_ACCOUNT.address}:{signature_hex}"
        print("✅ Final Header (X-Flashbots-Signature):", header_value)

        return header_value
