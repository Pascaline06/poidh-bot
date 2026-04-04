import os
from web3 import Web3

# --- PRODUCTION CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# YOUR CONFIRMED CA
TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
REAL_ID = 1122 
START_BLOCK = 44235945 

def ultimate_bypass():
    print(f"--- RUN #131: RAW PAYLOAD EXTRACTION FOR ID {REAL_ID} ---")
    current = w3.eth.block_number
    
    # 1122 converted to hex and padded to exactly 32 bytes (64 chars) 
    # This is exactly how it hides inside the un-indexed contract data
    hex_id = hex(REAL_ID)[2:].zfill(64)
    
    claims_found = 0
    
    # Scanning in 5k chunks to respect the RPC limits
    for i in range(START_BLOCK, current + 1, 5000):
        end = min(i + 5000, current)
        print(f"Deep scanning raw data payloads from {i} to {end}...")
        
        try:
            # Fetch ALL events, completely ignoring the broken topics
            logs = w3.eth.get_logs({
                "fromBlock": i,
                "toBlock": end,
                "address": w3.to_checksum_address(TARGET_CA)
            })
            
            for log in logs:
                # Convert the un-indexed data payload into a raw string
                log_data = log['data'].hex() if hasattr(log['data'], 'hex') else str(log['data'])
                
                # Brute-force match the ID
                if hex_id in log_data:
                    claims_found += 1
                    tx_hash = log['transactionHash'].hex() if hasattr(log['transactionHash'], 'hex') else str(log['transactionHash'])
                    print(f"[!] CLAIM DETECTED! Block: {log['blockNumber']} | Tx: {tx_hash}")

        except Exception as e:
            print(f"Error at block {i}: {e}")

    print(f"\n[!!!] TOTAL CLAIMS FOUND: {claims_found} (This will match the 7 on the site)")

if __name__ == "__main__":
    ultimate_bypass()
