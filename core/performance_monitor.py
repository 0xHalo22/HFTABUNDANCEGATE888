
import time
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.detection_times = []
        self.submission_times = []
        self.total_processed = 0
        self.profitable_found = 0
        
    def start_detection_timer(self):
        return time.time()
    
    def end_detection_timer(self, start_time):
        detection_time = time.time() - start_time
        self.detection_times.append(detection_time)
        return detection_time
    
    def record_submission(self, submission_time):
        self.submission_times.append(submission_time)
    
    def record_transaction_processed(self):
        self.total_processed += 1
    
    def record_profitable_opportunity(self):
        self.profitable_found += 1
    
    def get_stats(self):
        if not self.detection_times:
            return "No performance data available"
        
        avg_detection = sum(self.detection_times) / len(self.detection_times)
        avg_submission = sum(self.submission_times) / len(self.submission_times) if self.submission_times else 0
        
        profit_rate = (self.profitable_found / self.total_processed * 100) if self.total_processed > 0 else 0
        
        return {
            "total_processed": self.total_processed,
            "profitable_found": self.profitable_found,
            "profit_rate_percent": round(profit_rate, 2),
            "avg_detection_time_ms": round(avg_detection * 1000, 2),
            "avg_submission_time_ms": round(avg_submission * 1000, 2),
            "fastest_detection_ms": round(min(self.detection_times) * 1000, 2),
            "slowest_detection_ms": round(max(self.detection_times) * 1000, 2)
        }
    
    def print_stats(self):
        stats = self.get_stats()
        if isinstance(stats, str):
            print(stats)
            return
        
        print(f"\n📊 PERFORMANCE STATS:")
        print(f"  📈 Transactions processed: {stats['total_processed']}")
        print(f"  💰 Profitable opportunities: {stats['profitable_found']}")
        print(f"  📊 Profit rate: {stats['profit_rate_percent']}%")
        print(f"  ⚡ Avg detection time: {stats['avg_detection_time_ms']}ms")
        print(f"  🚀 Avg submission time: {stats['avg_submission_time_ms']}ms")
        print(f"  🏃 Fastest detection: {stats['fastest_detection_ms']}ms")
        print(f"  🐌 Slowest detection: {stats['slowest_detection_ms']}ms")

# Global monitor instance
monitor = PerformanceMonitor()
