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
    
    # Filter 1: Very small minimum for testing (0.001 ETH = ~$4)
    min_value_wei = 1000000000000000  # 0.001 ETH in wei
    if value < min_value_wei:
        print(f"  ❌ SKIP: Value too low ({value / 1e18:.6f} ETH < 0.001 ETH)")
        return False
    
    # Filter 2: Expanded DEX addresses (more inclusive)
    known_dex_addresses = {
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router
        "0xf164fc0ec4e93095b804a4795bbe1e041497b92a",  # Uniswap V2 Router (old)
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",  # Uniswap V3 Router 2
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router
        "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",  # SushiSwap Router V2
        "0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b",  # Uniswap Universal Router
        "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",  # Uniswap Universal Router V2
        "0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae",  # Lido stETH
        "0x663dc15d3c1ac63ff12e45ab68fea3f0a883c251",  # Additional DEX
        "0xa26148ae51fa8e787df319c04137602cc018b521",  # Additional DEX
        "0x25844d76468ca491cf9b3d8d3aec958200ca99d1",  # Additional DEX
        "0x101352f507bd5103b3c23fd39899165cf0c4d8c8",  # Additional DEX
        "0xbea9f7fd27f4ee20066f18def0bc586ec221055a",  # Additional DEX
    }
    
    if to_address not in known_dex_addresses:
        print(f"  ❌ SKIP: Not a known DEX address")
        return False
    
    # Filter 3: Higher gas price tolerance (200 gwei instead of 100)
    max_gas_price = 200000000000  # 200 gwei (was 100)
    if gas_price > max_gas_price:
        print(f"  ❌ SKIP: Gas price too high ({gas_price / 1e9:.1f} gwei > 200 gwei)")
        return False
    
    # 🎯 PASSED ALL FILTERS!
    print(f"  ✅ VALID DEX TX: PASSED ALL FILTERS!")
    print(f"  🚀 Sending to execution pipeline...")
    return True
