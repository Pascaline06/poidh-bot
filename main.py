import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
TARGET_ID = 136
# Exact birth block we found
START_BLOCK = 44235945 

def catch_all_search():
    print(f"--- RUN #114: CATCH-ALL SEARCH FOR BOUNTY {TARGET_ID} ---")
    current_block = w3.eth.block_number
    
    # We pad the ID to search the blockchain's raw data
    target_hex = w3.to_hex(w3.to_bytes(TARGET_ID).rjust(32, b'\0'))
    
    try:
        print(f"Checking every event for ID 136 from {START_BLOCK} to {current_block}...")
        # This looks for the ID 136 in ANY of the first three indexed topics
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [[None, target_hex, None, None]] 
        })

        if not logs:
            print(f"[!] Zero events found for ID 136. This suggests no claims have been submitted yet.")
            return

        print(f"[!] SUCCESS: Found {len(logs)} interactions involving ID 136!")
        for log in logs:
            event_hash = log['topics'][0].hex()
            print(f"-> Found event {event_hash[:10]}... in block {log['blockNumber']}")
            # If we find it, we can instantly pull the image in the next step
            
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    catch_all_search()
