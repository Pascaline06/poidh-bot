import time
from web3 import Web3

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_BOUNTY_ID = 136

# 2. THE WINDOW (Based on your "20 hours ago" screenshot)
# Block 44222459 was 20 hours ago.
START_BLOCK = 44220000 
END_BLOCK = 44240000 
CHUNK_SIZE = 1000 # Keeps it safe from "Payload Too Large" errors

def run_broad_scan():
    if not w3.is_connected(): return
    
    print(f"--- SCANNING FOR ALL CLAIMS AROUND BLOCK {START_BLOCK} ---")

    current_start = START_BLOCK
    while current_start < END_BLOCK:
        current_end = min(current_start + CHUNK_SIZE, END_BLOCK)
        
        try:
            # We ONLY filter by the Event Signature (Topic 0)
            # This avoids any "Topic Index" confusion
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG] 
            })

            for log in logs:
                # Check Topic 3 (The Bounty ID) inside the code
                try:
                    bounty_id_hex = log['topics'][3].hex()
                    found_id = int(bounty_id_hex, 16)
                    
                    if found_id == TARGET_BOUNTY_ID:
                        print(f"\n[!!!] MATCH FOUND: Bounty {found_id}")
                        print(f"Block: {log['blockNumber']}")
                        print(f"TX: https://basescan.org/tx/{log['transactionHash'].hex()}")
                    else:
                        # Just to show you the bot is actually working:
                        print(f"Found a claim for Bounty {found_id} (Skipping...)")
                except:
                    continue

        except Exception as e:
            print(f"Error in chunk {current_start}: {e}")
            time.sleep(1)

        current_start = current_end + 1

    print("\n--- SCAN COMPLETE ---")

if __name__ == "__main__":
    run_broad_scan()
