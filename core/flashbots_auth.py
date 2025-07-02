
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

    # DEBUG: Check address consistency
    print("🔍 ADDRESS VERIFICATION:")
    print("  SEARCHER_ACCOUNT.address:", SEARCHER_ACCOUNT.address)
    
    # TRY APPROACH 1: Direct signing using raw private key
    try:
        from eth_keys import keys
        
        # Get raw private key from environment (remove 0x prefix if present)
        raw_private_key = PRIVATE_KEY_SEARCHER
        if raw_private_key.startswith('0x'):
            raw_private_key = raw_private_key[2:]
        
        # Convert to bytes and create PrivateKey object
        private_key_bytes = bytes.fromhex(raw_private_key)
        private_key = keys.PrivateKey(private_key_bytes)
        
        # Verify address derivation
        derived_address = private_key.public_key.to_checksum_address()
        print("  Raw key derived address:", derived_address)
        print("  Addresses match:", derived_address == SEARCHER_ACCOUNT.address)
        
        # Sign the digest directly
        signature = private_key.sign_msg_hash(digest)
        
        # Convert to 65-byte format: r (32) + s (32) + v (1)
        signature_hex = '0x' + signature.to_bytes().hex()
        
        print("✍️ RAW KEY Direct Signature (65-byte):", signature_hex)
        print("🔐 Using Address:", derived_address)
        
        # Try different signature recovery formats
        print("🧪 SIGNATURE ANALYSIS:")
        sig_bytes = signature.to_bytes()
        print(f"  Signature length: {len(sig_bytes)} bytes")
        print(f"  R: 0x{sig_bytes[:32].hex()}")
        print(f"  S: 0x{sig_bytes[32:64].hex()}")
        print(f"  V: {sig_bytes[64]}")
        
        # Test signature recovery
        from eth_keys import keys as eth_keys
        recovered_pubkey = eth_keys.Signature(sig_bytes).recover_public_key_from_msg_hash(digest)
        recovered_address = recovered_pubkey.to_checksum_address()
        print(f"  Recovered address: {recovered_address}")
        print(f"  Recovery matches: {recovered_address == derived_address}")
        
        # Use the derived address (not SEARCHER_ACCOUNT.address) for header
        header_value = f"{derived_address}:{signature_hex}"
        print("✅ Final Header (X-Flashbots-Signature):", header_value)

        return header_value
        
    except Exception as e:
        print(f"❌ RAW KEY Direct signing failed: {e}")
        import traceback
        traceback.print_exc()

        # Step 4: Construct X-Flashbots-Signature header
        header_value = f"{SEARCHER_ACCOUNT.address}:{signature_hex}"
        print("✅ Final Header (X-Flashbots-Signature):", header_value)

        return header_value
        
    except Exception as e:
        print(f"❌ RAW KEY Direct signing failed: {e}")
        
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
