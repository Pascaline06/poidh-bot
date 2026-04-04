import os
from web3 import Web3

RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# The most active CA from your discovery screenshot
PROBABLE_CA = "0x1a90Cb21b770d170821C0EBF56ce6Ffb2942e5D4"
TARGET_ID = 136

def final_attempt():
    print(f"--- RUN #128: TESTING PROBABLE CA FOR ID {TARGET_ID} ---")
    current = w3.eth.block_number
    
    try:
        # Scan 10,000 blocks on the most likely candidate
        logs = w3.eth.get_logs({
            "fromBlock": current - 10000,
            "toBlock": "latest",
            "address": w3.to_checksum_address(PROBABLE_CA)
        })
        
        print(f"Found {len(logs)} total events on this contract.")
        id_counts = {}
        for log in logs:
            if len(log['topics']) > 1:
                real_id = int(log['topics'][1].hex(), 16)
                id_counts[real_id] = id_counts.get(real_id, 0) + 1
        
        for b_id, count in id_counts.items():
            if b_id == TARGET_ID:
                print(f"[!!!] SUCCESS: Found {count} claims for ID 136 on this contract!")
                return
        
        print("[X] 136 not found here. Printing existing IDs for comparison:")
        print(id_counts)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_attempt()
