def is_valid_tx(tx):
    # LIVE mode tx filter — allow all for now
    print(f"🔍 [TX FILTER - LIVE] Allowing tx: {tx['hash'].hex()} -> to: {tx.get('to')}")
    return True True
