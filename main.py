import os
import time
from web3 import Web3

# --- CONFIGURATION ---
# Use your Alchemy or QuickNode URL if public ones keep failing
RPC_URL = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Data extracted from your Basescan logs
TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
REAL_ID = 136  # The on-chain ID for UI 1122
START_BLOCK = 44235945 # Block where bounty was created

def run_poidh_bot():
    print(f"--- RUN #133: TARGETING BOUNTY {REAL_ID} ---")
    
    if not w3.is_connected():
        print("Failed to connect to Base RPC.")
        return

    # Manually pad the ID to 32 bytes (64 hex characters)
    # This is critical for Topic filters to match on-chain data
    hex_id = hex(REAL_ID)[2:].zfill(64)
    topic_id = f"0x{hex_id}"
    
    current_block = w3.eth.block_number
    print(f"Scanning from {START_BLOCK} to {current_block}...")

    try:
        # We use a sparse topic list to avoid indexing mismatches
        # [Event Signature, ClaimID (null), Issuer (null), BountyID (Target)]
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": "latest",
            "address": w3.to_checksum_address(TARGET_CA),
            "topics": [EVENT_SIG, None, None, topic_id]
        })

        if not logs:
            print(f"[!] No claims found for ID {REAL_ID}. Double-check block range.")
        else:
            print(f"Success! Found {len(logs)} claims on-chain.")
            for i, log in enumerate(logs, 1):
                tx_hash = log['transactionHash'].hex()
                print(f"Claim {i}: https://basescan.org/tx/{tx_hash}")

    except Exception as e:
        if "413" in str(e):
            print("Error: Payload too large. Reduce the block range.")
        elif "429" in str(e):
            print("Error: Rate limited. Use a private RPC key.")
        else:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_poidh_bot()
