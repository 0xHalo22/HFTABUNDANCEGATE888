def is_valid_tx(tx):
    """Enhanced transaction filter for profitable opportunities"""
    
    # Basic checks
    tx_hash = tx['hash'].hex() if isinstance(tx['hash'], bytes) else tx['hash']
    to_address = tx.get('to', '').lower()
    value = tx.get('value', 0)
    
    # Filter 1: MUCH lower minimum for testing (0.01 ETH = ~$40)
    min_value_wei = 10000000000000000  # 0.01 ETH in wei (was 0.05)
    if value < min_value_wei:
        print(f"⛔ [FILTER] Low value tx: {value / 1e18:.6f} ETH < 0.01 ETH threshold")
        return False
    
    # Filter 2: Expanded DEX addresses
    known_dex_addresses = {
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router
        "0xf164fc0ec4e93095b804a4795bbe1e041497b92a",  # Uniswap V2 Router (old)
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",  # Uniswap V3 Router 2
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router
        "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",  # SushiSwap Router V2
        "0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b",  # Uniswap Universal Router
        "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",  # Uniswap Universal Router V2
    }
    
    if to_address not in known_dex_addresses:
        print(f"⛔ [FILTER] Not targeting known DEX: {to_address}")
        return False
    
    # Filter 3: Higher gas price tolerance (200 gwei instead of 100)
    gas_price = tx.get('gasPrice', 0)
    max_gas_price = 200000000000  # 200 gwei (was 100)
    if gas_price > max_gas_price:
        print(f"⛔ [FILTER] Gas price too high: {gas_price / 1e9:.1f} gwei > 200 gwei")
        return False
    
    print(f"✅ [FILTER] Valid opportunity: {tx_hash} -> {to_address} ({value / 1e18:.3f} ETH)")
    return True
