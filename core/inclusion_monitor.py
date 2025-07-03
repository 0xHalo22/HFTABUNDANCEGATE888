
import asyncio
import time
from web3 import Web3

class InclusionMonitor:
    def __init__(self, w3):
        self.w3 = w3
        self.pending_bundles = {}
        self.total_profit_realized = 0.0
        self.total_bribes_paid = 0.0
        
    def track_bundle(self, bundle_hash, target_blocks, victim_tx_hash, bribe_amount, estimated_profit):
        """Track a bundle for inclusion monitoring"""
        self.pending_bundles[bundle_hash] = {
            "target_blocks": target_blocks,
            "victim_tx_hash": victim_tx_hash,
            "bribe_amount": bribe_amount,
            "estimated_profit": estimated_profit,
            "submitted_at": self.w3.eth.block_number,
            "timestamp": time.time()
        }
        print(f"🔍 TRACKING: Bundle {bundle_hash[:16]}... for blocks {target_blocks}")
    
    async def check_inclusions(self):
        """Check if any pending bundles got included and calculate real profits"""
        current_block = self.w3.eth.block_number
        
        for bundle_hash, info in list(self.pending_bundles.items()):
            target_blocks = info["target_blocks"]
            victim_tx_hash = info["victim_tx_hash"]
            
            # Check if any target block has passed
            max_target = max(target_blocks)
            if current_block > max_target:
                included = False
                inclusion_block = None
                
                # Check each target block for victim transaction
                for target_block in target_blocks:
                    try:
                        block = self.w3.eth.get_block(target_block, full_transactions=True)
                        
                        # Check if victim transaction was included
                        for tx in block.transactions:
                            if tx.hash.hex() == victim_tx_hash:
                                included = True
                                inclusion_block = target_block
                                break
                        
                        if included:
                            break
                            
                    except Exception as e:
                        print(f"❌ Error checking block {target_block}: {e}")
                
                # Process result
                if included:
                    profit = info["estimated_profit"]
                    bribe = info["bribe_amount"]
                    net_profit = profit - bribe
                    
                    self.total_profit_realized += net_profit
                    self.total_bribes_paid += bribe
                    
                    print(f"🎉 BUNDLE INCLUDED! Block {inclusion_block}")
                    print(f"💰 REALIZED PROFIT: {net_profit:.6f} ETH")
                    print(f"📊 TOTAL SESSION PROFIT: {self.total_profit_realized:.6f} ETH")
                else:
                    print(f"❌ Bundle {bundle_hash[:16]}... MISSED (blocks {target_blocks})")
                
                # Remove from tracking
                del self.pending_bundles[bundle_hash]
        
    def get_session_stats(self):
        """Get current session profit statistics"""
        return {
            "total_profit_realized": self.total_profit_realized,
            "total_bribes_paid": self.total_bribes_paid,
            "pending_bundles": len(self.pending_bundles),
            "net_session_profit": self.total_profit_realized
        }
