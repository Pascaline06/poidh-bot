import os
import requests
from web3 import Web3

# --- FINAL HARD CONSTRAINTS ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# YOUR CONFIRMED CA FROM BASESCAN
TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
TARGET_ID_HEX = "0x0000000000000000000000000000000000000000000000000000000000000088" # Hex for 136

def scan_raw_transactions():
    print(f"--- RUN #129: RAW TRANSACTION DECODE FOR CA {TARGET_CA} ---")
    current_block = w3.eth.block_number
    
    # We scan the last 5,000 blocks specifically for interactions with this CA
    # This bypasses the 'Event' system which is currently failing us.
    for i in range(current_block - 5000, current_block + 1):
        block = w3.eth.get_block(i, full_transactions=True)
        for tx in block.transactions:
            if tx.to and tx.to.lower() == TARGET_CA.lower():
                # Check if the transaction 'input' data contains our Bounty ID (136)
                if TARGET_ID_HEX in tx.input:
                    print(f"[!] MATCH FOUND: Transaction {tx.hash.hex()} in Block {i}")
                    # This confirms the transaction exists and we can now pull the metadata
    
    print("Scan complete. If matches appeared above, the bot is now tracking the right data.")

if __name__ == "__main__":
    scan_raw_transactions()
