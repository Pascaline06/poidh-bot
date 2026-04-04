import os
import requests
import base64
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# THE CONFIRMED CA AND THE REAL BLOCKCHAIN ID
CORRECT_CA = "0x5555Fa783936C260f77385b4e153B9725feF1719"
REAL_ID = 1122 

def final_judgment():
    print(f"--- RUN #122: SCANNING REAL ID {REAL_ID} ---")
    
    # The topic must be the hex version of 1122, padded to 32 bytes
    id_topic = w3.to_hex(w3.to_bytes(REAL_ID).rjust(32, b'\0'))
    
    try:
        # We look back 20,000 blocks to ensure we catch all 7 transactions
        current = w3.eth.block_number
        logs = w3.eth.get_logs({
            "fromBlock": current - 20000,
            "toBlock": "latest",
            "address": w3.to_checksum_address(CORRECT_CA),
            "topics": [None, id_topic] 
        })

        if not logs:
            print(f"[!] Still no logs for ID {REAL_ID}. Checking raw contract activity...")
            return

        print(f"[!] SUCCESS! Found {len(logs)} claims for the physical book bounty.")
        # ... (Judgment logic goes here) ...

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_judgment()
