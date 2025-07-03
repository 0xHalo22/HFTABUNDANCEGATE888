def is_valid_tx(tx):
    """Enhanced transaction filter for profitable opportunities"""
    
    # Basic checks
    tx_hash = tx['hash'].hex() if isinstance(tx['hash'], bytes) else tx['hash']
    to_address = tx.get('to', '').lower()
    value = tx.get('value', 0)
    
    # Filter 1: Minimum ETH value threshold (0.05 ETH = ~$200 at current prices)
    min_value_wei = 50000000000000000  # 0.05 ETH in wei
    if value < min_value_wei:
        print(f"⛔ [FILTER] Low value tx: {value / 1e18:.6f} ETH < 0.05 ETH threshold")
        return False
    
    # Filter 2: Known DEX addresses (Uniswap V2/V3, SushiSwap, etc.)
    known_dex_addresses = {
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router
        "0xf164fc0ec4e93095b804a4795bbe1e041497b92a",  # Uniswap V2 Router (old)
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router
    }
    
    if to_address not in known_dex_addresses:
        print(f"⛔ [FILTER] Not targeting known DEX: {to_address}")
        return False
    
    # Filter 3: Gas price check (avoid txs with extremely high gas that indicate competition)
    gas_price = tx.get('gasPrice', 0)
    max_gas_price = 100000000000  # 100 gwei
    if gas_price > max_gas_price:
        print(f"⛔ [FILTER] Gas price too high: {gas_price / 1e9:.1f} gwei > 100 gwei")
        return False
    
    print(f"✅ [FILTER] Valid opportunity: {tx_hash} -> {to_address} ({value / 1e18:.3f} ETH)")
    return True
