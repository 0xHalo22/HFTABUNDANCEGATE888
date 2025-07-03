
import asyncio
from web3 import Web3

class BundleMonitor:
    def __init__(self, w3):
        self.w3 = w3
        self.pending_bundles = {}
    
    def track_bundle(self, bundle_hash, target_block, victim_tx_hash):
        """Track a bundle for inclusion monitoring"""
        self.pending_bundles[bundle_hash] = {
            "target_block": target_block,
            "victim_tx_hash": victim_tx_hash,
            "submitted_at": self.w3.eth.block_number
        }
        print(f"📊 Tracking bundle {bundle_hash[:16]}... for block {target_block}")
    
    async def check_inclusions(self):
        """Check if any pending bundles got included"""
        current_block = self.w3.eth.block_number
        
        for bundle_hash, info in list(self.pending_bundles.items()):
            target_block = info["target_block"]
            
            # If we're past the target block, check if it was included
            if current_block > target_block:
                try:
                    block = self.w3.eth.get_block(target_block, full_transactions=True)
                    victim_tx_hash = info["victim_tx_hash"]
                    
                    # Check if victim transaction was included
                    included = any(tx.hash.hex() == victim_tx_hash for tx in block.transactions)
                    
                    if included:
                        print(f"🎉 BUNDLE INCLUDED! Block {target_block}, Hash: {bundle_hash[:16]}...")
                        # TODO: Calculate actual profit from block data
                    else:
                        print(f"❌ Bundle missed: Block {target_block}, Hash: {bundle_hash[:16]}...")
                    
                    # Remove from tracking
                    del self.pending_bundles[bundle_hash]
                    
                except Exception as e:
                    print(f"❌ Error checking bundle inclusion: {e}")

monitor = BundleMonitor(None)  # Will be initialized with w3 in main
