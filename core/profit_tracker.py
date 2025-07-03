
import time
import json
from collections import defaultdict

class ProfitTracker:
    def __init__(self):
        self.session_start = time.time()
        self.total_submitted = 0
        self.total_included = 0
        self.total_profit_realized = 0.0
        self.total_bribes_paid = 0.0
        self.total_gas_spent = 0.0
        
        self.simulation_results = []
        self.bundle_results = []
        
        # Performance metrics
        self.profitable_simulations = 0
        self.unprofitable_simulations = 0
        self.avg_simulation_time = 0.0
        
    def record_simulation(self, result, simulation_time):
        """Record pre-bundle simulation results"""
        self.simulation_results.append({
            "timestamp": time.time(),
            "profitable": result.get("profitable", False),
            "estimated_profit": result.get("estimated_profit", 0),
            "reason": result.get("reason", ""),
            "simulation_time": simulation_time
        })
        
        if result.get("profitable"):
            self.profitable_simulations += 1
        else:
            self.unprofitable_simulations += 1
            
        # Update average simulation time
        total_time = sum(r["simulation_time"] for r in self.simulation_results)
        self.avg_simulation_time = total_time / len(self.simulation_results)
        
    def record_bundle_submission(self, bundle_hash, estimated_profit, bribe_amount):
        """Record bundle submission"""
        self.total_submitted += 1
        self.bundle_results.append({
            "timestamp": time.time(),
            "bundle_hash": bundle_hash,
            "estimated_profit": estimated_profit,
            "bribe_amount": bribe_amount,
            "status": "submitted"
        })
        
    def record_bundle_inclusion(self, bundle_hash, actual_profit, gas_cost):
        """Record successful bundle inclusion"""
        self.total_included += 1
        self.total_profit_realized += actual_profit
        self.total_gas_spent += gas_cost
        
        # Find and update the bundle record
        for bundle in self.bundle_results:
            if bundle["bundle_hash"] == bundle_hash:
                bundle["status"] = "included"
                bundle["actual_profit"] = actual_profit
                bundle["gas_cost"] = gas_cost
                break
    
    def record_bribe_payment(self, amount):
        """Record bribe payment"""
        self.total_bribes_paid += amount
    
    def get_performance_stats(self):
        """Get comprehensive performance statistics"""
        session_duration = time.time() - self.session_start
        inclusion_rate = (self.total_included / self.total_submitted * 100) if self.total_submitted > 0 else 0
        simulation_success_rate = (self.profitable_simulations / (self.profitable_simulations + self.unprofitable_simulations) * 100) if (self.profitable_simulations + self.unprofitable_simulations) > 0 else 0
        
        net_profit = self.total_profit_realized - self.total_bribes_paid - self.total_gas_spent
        
        return {
            "session_duration_minutes": session_duration / 60,
            "total_simulations": len(self.simulation_results),
            "profitable_simulations": self.profitable_simulations,
            "simulation_success_rate": simulation_success_rate,
            "avg_simulation_time_ms": self.avg_simulation_time * 1000,
            "total_bundles_submitted": self.total_submitted,
            "total_bundles_included": self.total_included,
            "inclusion_rate_percent": inclusion_rate,
            "total_profit_realized": self.total_profit_realized,
            "total_bribes_paid": self.total_bribes_paid,
            "total_gas_spent": self.total_gas_spent,
            "net_session_profit": net_profit,
            "roi_percent": (net_profit / (self.total_bribes_paid + self.total_gas_spent) * 100) if (self.total_bribes_paid + self.total_gas_spent) > 0 else 0
        }
    
    def print_live_stats(self):
        """Print live performance statistics"""
        stats = self.get_performance_stats()
        
        print(f"\n🎯 LIVE PROFIT TRACKER DASHBOARD:")
        print(f"  ⏱️  Session Duration: {stats['session_duration_minutes']:.1f} minutes")
        print(f"  🧮 Simulations: {stats['total_simulations']} total, {stats['profitable_simulations']} profitable ({stats['simulation_success_rate']:.1f}%)")
        print(f"  ⚡ Avg Simulation Time: {stats['avg_simulation_time_ms']:.1f}ms")
        print(f"  📦 Bundles: {stats['total_bundles_submitted']} submitted, {stats['total_bundles_included']} included ({stats['inclusion_rate_percent']:.1f}%)")
        print(f"  💰 Profit Realized: {stats['total_profit_realized']:.6f} ETH")
        print(f"  🧮 Bribes Paid: {stats['total_bribes_paid']:.6f} ETH")
        print(f"  ⛽ Gas Spent: {stats['total_gas_spent']:.6f} ETH")
        print(f"  📊 NET PROFIT: {stats['net_session_profit']:.6f} ETH")
        print(f"  📈 ROI: {stats['roi_percent']:.1f}%")
        print(f"")

# Global tracker instance
profit_tracker = ProfitTracker()
