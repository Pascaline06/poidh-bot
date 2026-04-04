import os
import time
from web3 import Web3

# Use the public RPC but handle it delicately
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
REAL_ID = 136 
START_BLOCK = 44235945 # Block from your Basescan logs
CHUNK_SIZE = 2000 # Small chunks to avoid 'Payload Too Large'

def run_chunked_scan():
    print(f"--- RUN #135: CHUNKED SCAN FOR ID {REAL_ID} ---")
    topic_id = "0x" + hex(REAL_ID)[2:].zfill(64)
    latest_block = w3.eth.block_number
    
    current_start = START_BLOCK
    all_logs = []

    while current_start < latest_block:
        current_end = min(current_start + CHUNK_SIZE, latest_block)
        print(f"Checking blocks {current_start} to {current_end}...")
        
        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(TARGET_CA),
                "topics": [EVENT_SIG, None, None, topic_id]
            })
            all_logs.extend(logs)
            # Short sleep to prevent '429 Too Many Requests'
            time.sleep(0.2) 
        except Exception as e:
            print(f"Chunk failed: {e}")
            
        current_start = current_end + 1

    print(f"\nFINAL RESULT: Found {len(all_logs)} claims.")
    for log in all_logs:
        print(f"Claim TX: https://basescan.org/tx/{log['transactionHash'].hex()}")

if __name__ == "__main__":
    run_chunked_scan()
