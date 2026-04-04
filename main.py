import os
from web3 import Web3

# --- HARD CONSTRAINTS ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# THE CA YOU PROVIDED
TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"

def reveal_the_truth():
    print(f"--- RUN #127: REVEALING ACTUAL ON-CHAIN IDs ---")
    current = w3.eth.block_number
    
    try:
        # Search the last 10,000 blocks for ANY claim on this contract
        logs = w3.eth.get_logs({
            "fromBlock": current - 10000,
            "toBlock": "latest",
            "address": w3.to_checksum_address(TARGET_CA)
        })
        
        if not logs:
            print("[X] No activity found on this CA. The address is likely wrong.")
            return

        print(f"Found {len(logs)} total events. Extracting IDs...")
        id_counts = {}
        for log in logs:
            # Smart contracts usually put the Bounty ID in the second topic
            if len(log['topics']) > 1:
                real_id = int(log['topics'][1].hex(), 16)
                id_counts[real_id] = id_counts.get(real_id, 0) + 1
        
        print("\nOn-Chain Bounty IDs found recently:")
        for b_id, count in id_counts.items():
            match_status = " <--- TARGET FOUND!" if count >= 6 else ""
            print(f"Bounty ID {b_id}: {count} claims{match_status}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reveal_the_truth()
