
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
    Signs the canonical JSON payload for Flashbots using the standard method.
    Based on Flashbots example bot implementation.
    
    Args:
        payload (str): Canonical JSON string

    Returns:
        str: X-Flashbots-Signature header value in format "0xAddress:0xSignature"
    """
    print("🔄 [SIGNATURE] Starting Flashbots signature process...")
    
    # Step 1: keccak256 hash of UTF-8 encoded JSON string  
    digest = Web3.keccak(payload.encode("utf-8"))
    print("🔑 Payload hash:", digest.hex())
    
    # Step 2: Use standard EIP-191 signing (like the example bot)
    message = encode_defunct(hexstr=digest.hex())
    signed = SEARCHER_ACCOUNT.sign_message(message)
    signature_hex = signed.signature.hex()
    
    print("✍️ Signature:", signature_hex)
    print("🔐 Signer Address:", SEARCHER_ACCOUNT.address)
    
    # Step 3: Construct header
    header_value = f"{SEARCHER_ACCOUNT.address}:{signature_hex}"
    print("✅ X-Flashbots-Signature:", header_value)
    
    return header_value
