import csv
import time
from datetime import datetime

class Executor:
    def __init__(self):
        pass

    async def handle_profitable_trade(self, tx):
        try:
            # Extract data from the tx object
            token_address = tx.get("token_address", "unknown")
            profit = tx.get("profit", 0)
            gas_used = tx.get("gas_used", 0)
            status = tx.get("status", "unknown")

            # Create timestamp
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            print("[✔️] Trade detected:", {
                "timestamp": timestamp,
                "token_address": token_address,
                "profit": profit,
                "gas_used": gas_used,
                "status": status
            })

            # Only write successful trades
            if status.lower() != "success":
                print("[⚠️] Trade not successful, skipping CSV write.")
                return

            # Write to CSV
            print("[💾] Attempting to write to trade_log.csv...")
            with open("data/trade_log.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, token_address, profit, gas_used, status])
            print("[✅] Trade successfully written to CSV.")

        except Exception as e:
            print("[❌] Exception during trade handling:", e)
