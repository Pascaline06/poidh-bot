import os
import requests
import base64
from web3 import Web3

# --- HARD CONSTRAINTS ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# THE CA YOU PROVIDED
TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
TARGET_ID = 136
# The birth block we confirmed earlier
START_BLOCK = 44235945 

def final_fix():
    print(f"--- RUN #126: MANUAL OVERRIDE SCAN ---")
    current = w3.eth.block_number
    # Search in 5000 block chunks to prevent the 413 Payload Error
    
    found_claims = []
    
    for i in range(START_BLOCK, current + 1, 5000):
        end = min(i + 5000, current)
        print(f"Deep scanning blocks {i} to {end}...")
        
        try:
            # We fetch ALL logs from your CA to ensure we don't miss anything
            logs = w3.eth.get_logs({
                "fromBlock": i,
                "toBlock": end,
                "address": w3.to_checksum_address(TARGET_CA)
            })
            
            for log in logs:
                # Check if the Bounty ID (136) is anywhere in the topics
                # 136 in hex is 0x88
                if any("00000088" in t.hex() for t in log['topics']):
                    found_claims.append(log)
                    print(f"[!] MATCH FOUND in block {log['blockNumber']}")

        except Exception as e:
            print(f"Error at block {i}: {e}")

    print(f"\n[!] TOTAL CLAIMS FOUND FOR ID 136: {len(found_claims)}")
    # If this finds 6, the loop is broken.

if __name__ == "__main__":
    final_fix()
