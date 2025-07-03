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

    # 🚀 ENHANCED FILTERING - Your buddy's recommendations implemented!
    
    # CRITICAL: Minimum victim value check (0.1 ETH threshold)
    MIN_VICTIM_VALUE = 1e17  # 0.1 ETH in wei
    if value < MIN_VICTIM_VALUE and value > 0:
        print(f"  ❌ VICTIM TOO SMALL: {value / 1e18:.6f} ETH < 0.1 ETH minimum")
        return False
    
    # Gas price sanity check - avoid transactions with extremely low gas
    MIN_GAS_PRICE = 1e8  # 0.1 gwei minimum
    if gas_price < MIN_GAS_PRICE:
        print(f"  ❌ GAS TOO LOW: {gas_price / 1e9:.1f} gwei < 0.1 gwei minimum")
        return False
    
    print(f"  ✅ VICTIM QUALIFIES: {value / 1e18:.6f} ETH value, {gas_price / 1e9:.1f} gwei gas")

    # Filter 1: OFFICIAL VERIFIED DEX ROUTERS ONLY (From Security Audit)
    known_dex_addresses = {
        # 🟢 Uniswap Routers (Official Verified List)
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router02 (Most common)
        "0xf164fc0ec4e93095b804a4795bbe1e041497b92a",  # Uniswap V2 Legacy Router (Deprecated but live)
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router (Single-hop)
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",  # Uniswap V3 Router 2 (Multicall & complex routing)
        "0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b",  # Uniswap Universal Router (Next-gen)
        "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",  # Universal Router V2 (ETH & Base)
        
        # 🟢 SushiSwap Routers (Official Verified List)
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router V1 (Legacy)
        "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",  # SushiSwap Router V2
        
        # 🟢 1inch Aggregator (High Volume)
        "0x1111111254eeb25477b68fb85ed929f73a960582",  # 1inch V5 Router
        "0x1111111254fb6c44bac0bed2854e76f90643097d",  # 1inch V4 Router
        "0x111111125421ca6dc452d289314280a0f8842a65",  # 1inch V3 Router
        
        # 🟢 Paraswap (Popular Aggregator)
        "0xdef171fe48cf0115b1d80b88dc8eab59176fee57",  # Paraswap V5 Augustus
        "0x216b4b4ba9f3e719726886d34a177484278bfcae",  # Paraswap V4
        
        # 🟢 Curve Finance
        "0x99a58482bd75cbab83b27ec03ca68ff489b5788f",  # Curve Router
        
        # 🟢 Balancer V2
        "0xba12222222228d8ba445958a75a0704d566bf2c8",  # Balancer Vault
        
        # 🟢 0x Protocol
        "0xdef1c0ded9bec7f1a1670819833240f027b25eff",  # 0x Exchange Proxy
        
        # 🟢 Kyber Network
        "0x6131b5fae19ea4f9d964eac0408e4408b66337b5",  # Kyber Router
        
        # 🟢 Additional Popular DEX Routers
        "0x881d40237659c251811cec9c364ef91dc08d300c",  # Metamask Swap Router
        "0x1111111254760f7ab3f16433eea9304126dcd199",  # 1inch V6 Router
        "0x9008d19f58aabd9ed0d60971565aa8510560ab41",  # CoW Protocol GPv2
        "0x74de5d4fcbf63e00296fd95d33236b9794016631",  # Matcha/0x Router
        "0x11111112542d85b3ef69ae05771c2dccff4faa26",  # 1inch Limit Order Protocol
        "0x1111111254fb6c44bac0bed2854e76f90643097d",  # 1inch V4 Router (backup)
        "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",  # Tokenlon Router
        "0x92be6adb6a12da0ca607f9d87db2f9978cd6ec3e",  # Tokenlon Router V2
        "0x1a1ec25dc08e98e5e93f1104b5e5cdd298707d31",  # Airswap Router
        "0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1"   # Ganache Test Router
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