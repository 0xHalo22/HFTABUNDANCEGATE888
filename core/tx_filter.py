def is_valid_tx(tx):
    """Enhanced transaction filter for profitable opportunities"""

    # Basic checks
    tx_hash = tx['hash'].hex() if isinstance(tx['hash'], bytes) else tx['hash']
    to_address = tx.get('to', '').lower()
    value = tx.get('value', 0)
    gas_price = tx.get('gasPrice', 0)

    print(f"🔍 ANALYZING TX: {tx_hash[:16]}...")
    print(f"  📍 To: {to_address[:16]}...")
    print(f"  💰 Value: {value / 1e18:.6f} ETH")
    print(f"  ⛽ Gas Price: {gas_price / 1e9:.1f} gwei")

    # TESTING MODE: No value filter - any DEX transaction is profitable!
    print(f"  🧪 TEST MODE: Skipping value checks - all DEX txs are fair game!")

    # Filter 1: VERIFIED DEX ROUTERS ONLY (Security Audit Applied)
    known_dex_addresses = {
        # Uniswap Routers (Verified)
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router (Primary)
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",  # Uniswap V3 Router 2
        "0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b",  # Uniswap Universal Router V1
        "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",  # Uniswap Universal Router V2
        
        # SushiSwap Routers (Verified)
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router V1
        "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",  # SushiSwap Router V2
        
        # 1inch Router (Major Aggregator - Verified)
        "0x1111111254eeb25477b68fb85ed929f73a960582",  # 1inch V5 Router
        
        # 0x Protocol (Verified)
        "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  # 0x Exchange Proxy
    }
    
    # 🚨 SECURITY: Log unknown addresses for investigation
    if to_address not in known_dex_addresses and value > 0:
        print(f"  🚨 UNKNOWN ADDRESS DETECTED: {to_address}")
        print(f"     💰 Value: {value / 1e18:.6f} ETH - INVESTIGATE BEFORE ADDING!")
        print(f"     📝 Add to investigation log for manual review")

    if to_address not in known_dex_addresses:
        print(f"  ❌ SKIP: Not a known DEX address")
        return False

    # Filter 2: Higher gas price tolerance (200 gwei instead of 100)
    max_gas_price = 200000000000  # 200 gwei (was 100)
    if gas_price > max_gas_price:
        print(f"  ❌ SKIP: Gas price too high ({gas_price / 1e9:.1f} gwei > 200 gwei)")
        return False

    # 🎯 PASSED ALL FILTERS!
    print(f"  ✅ VALID DEX TX: PASSED ALL FILTERS!")
    print(f"  🚀 Sending to execution pipeline...")
    return True