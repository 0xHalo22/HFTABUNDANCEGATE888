import asyncio
from core.simulator import simulate_sandwich_bundle
from core.tx_filter import is_valid_tx
from core.profit_tracker import profit_tracker
from core.inclusion_monitor import initialize_monitor, get_inclusion_monitor

async def listen_for_swaps(w3):
    print("🚨 Starting ETH-only HFT sniper live...")
    print("🔌 Connecting to WebSocket provider...")
    print("🔍 Listening for new pending transactions...")
    
    # Initialize inclusion monitoring
    monitor = initialize_monitor(w3)
    print("🔍 Inclusion monitoring system activated!")

    tx_filter = w3.eth.filter("pending")
    
    # Processing counters
    total_processed = 0
    valid_found = 0

    while True:
        try:
            pending_tx_hashes = tx_filter.get_new_entries()

            for tx_hash in pending_tx_hashes:
                try:
                    tx = w3.eth.get_transaction(tx_hash)
                    total_processed += 1

                    if is_valid_tx(tx):
                        valid_found += 1
                        print(f"🎯 EXECUTION TRIGGER! ({valid_found} valid / {total_processed} total)")
                        await simulate_sandwich_bundle(tx, w3)
                    
                    # Log stats every 100 transactions
                    if total_processed % 100 == 0:
                        success_rate = (valid_found / total_processed) * 100
                        print(f"\n📊 SCANNING STATS: {valid_found}/{total_processed} valid ({success_rate:.2f}%)")
                        
                        # Print live profit tracking stats
                        profit_tracker.print_live_stats()
                        
                        # Check for bundle inclusions
                        monitor = get_inclusion_monitor()
                        if monitor:
                            await monitor.check_inclusions()
                            monitor.print_live_stats()

                except Exception as e:
                    print(f"❌ Error fetching tx data: {e}")

            await asyncio.sleep(1)  # Poll interval

        except Exception as e:
            print(f"❌ Error in mempool listener loop: {e}")
            await asyncio.sleep(5)
