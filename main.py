import os
from web3 import Web3

# --- PRODUCTION CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# YOUR CONFIRMED CA & THE REAL ID FROM THE URL
TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
REAL_ID = 1122 
# Starting at birth block to ensure full coverage
BIRTH_BLOCK = 44235945 

def resolve_claims():
    print(f"--- RUN #130: FINAL RESOLUTION FOR ID {REAL_ID} ---")
    current = w3.eth.block_number
    
    # Format the ID for a topic search (Topic 1 is usually the Bounty ID)
    target_topic = w3.to_hex(w3.to_bytes(REAL_ID).rjust(32, b'\0'))
    
    # Scan in 5k chunks to bypass the 413 Payload Error
    for i in range(BIRTH_BLOCK, current + 1, 5000):
        end = min(i + 5000, current)
        print(f"Scanning blocks {i} to {end} for ID {REAL_ID}...")
        
        try:
            logs = w3.eth.get_logs({
                "fromBlock": i,
                "toBlock": end,
                "address": w3.to_checksum_address(TARGET_CA),
                "topics": [None, target_topic]
            })
            
            if logs:
                print(f"[!!!] SUCCESS: Found {len(logs)} claims for ID {REAL_ID}!")
                for log in logs:
                    print(f"  > Claim in Block: {log['blockNumber']}")
                return # We found them, stop scanning.

        except Exception as e:
            print(f"Error at block {i}: {e}")

if __name__ == "__main__":
    resolve_claims()
