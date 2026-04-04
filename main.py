import time
from web3 import Web3

# --- 1. CONFIGURATION ---
# Gateway to the Base Network
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# THE POIDH CONTRACT (Verified from your screenshot)
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"

# ClaimCreated Event Signature
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"

# On-chain Bounty ID (Bounty 1122 = ID 136)
BOUNTY_ID = 136

# YESTERDAY'S RANGE (April 3, 2026)
# Current blocks are ~44.24M. This starts roughly 30 hours ago.
START_BLOCK = 44150000 
END_BLOCK = 44250000
CHUNK_SIZE = 1000  # Small chunks to prevent "413 Payload Too Large" error

def run_claim_finder():
    if not w3.is_connected():
        print("Error: Could not connect to Base RPC.")
        return

    print(f"--- RUN #146: SEARCHING FOR YESTERDAY'S CLAIMS (ID {BOUNTY_ID}) ---")
    
    # Format ID 136 to 32-byte hex (0x000...88)
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    
    current_start = START_BLOCK
    found_count = 0

    while current_start < END_BLOCK:
        current_end = min(current_start + CHUNK_SIZE, END_BLOCK)
        print(f"Scanning blocks {current_start} to {current_end}...")

        try:
            # THE FIX: Placing 'topic_id' in Topic 1 instead of Topic 3
            logs = w3.eth.get_logs({
                "from_block": current_start,
                "to_block": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG, topic_id]  # Indexing Topic 1
            })

            for log in logs:
                found_count += 1
                tx_hash = log['transactionHash'].hex()
                print(f"\n[!] SUCCESS: Found Claim #{found_count}")
                print(f"TX HASH: {tx_hash}")
                print(f"LINK: https://basescan.org/tx/{tx_hash}\n")

        except Exception as e:
            # Handles "413 Payload Too Large" or "429 Rate Limit"
            print(f"Error in chunk: {e}")
            time.sleep(1)

        current_start = current_end + 1
        time.sleep(0.1) # Small delay to respect RPC limits

    print(f"--- SCAN COMPLETE: {found_count} claims found ---")

if __name__ == "__main__":
    run_claim_finder()
