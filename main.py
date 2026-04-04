import os
import time
from web3 import Web3

RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
REAL_ID = 136 

# THE FIX: Start from block 10 million (roughly early 2024 on Base)
START_BLOCK = 10000000 
# Larger chunk size to move through 30+ million blocks quickly
CHUNK_SIZE = 50000 

def run_time_travel_scan():
    print(f"--- RUN #141: HISTORICAL SCAN FOR ID {REAL_ID} ---")
    
    # Correctly format the topic
    topic_id = "0x" + hex(REAL_ID)[2:].zfill(64)
    latest_block = w3.eth.block_number
    
    current_start = START_BLOCK
    all_logs = []

    print(f"Scanning from Block {START_BLOCK} to {latest_block}...")

    while current_start < latest_block:
        current_end = min(current_start + CHUNK_SIZE, latest_block)
        
        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(TARGET_CA),
                "topics": [EVENT_SIG, None, None, topic_id]
            })
            
            if logs:
                print(f"[*] FOUND {len(logs)} CLAIMS between blocks {current_start} and {current_end}!")
                all_logs.extend(logs)
                
            # Print a status update every 1 million blocks so we know it's not frozen
            if current_start % 1000000 < CHUNK_SIZE:
                print(f"Progress: Reached block {current_start}...")
                
            # Tiny sleep to avoid 429 rate limits
            time.sleep(0.1) 
            
        except Exception as e:
            print(f"Error at chunk {current_start}-{current_end}: {e}")
            # If 50k is too large for the node, it will print the error and we will know
            
        current_start = current_end + 1

    print(f"\n--- FINAL RESULT: Found {len(all_logs)} claims ---")
    for i, log in enumerate(all_logs, 1):
        print(f"Claim {i} TX: https://basescan.org/tx/{log['transactionHash'].hex()}")

if __name__ == "__main__":
    run_time_travel_scan()
