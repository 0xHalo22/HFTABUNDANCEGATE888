def is_sandwich_candidate(tx, w3):
    if tx.get("to") is None:
        return False
    if tx["to"].lower() not in [
        "0xf164fc0ec4e93095b804a4795bbe1e041497b92a",  # Uniswap V2
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3
    ]:
        return False
    if tx.get("value", 0) < w3.to_wei(0.01, "ether"):  # ~0.01 ETH
        return False
    return True
