import os
import requests
import base64
from web3 import Web3

# --- FINAL CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
REAL_ID = 1122 
BIRTH_BLOCK = 44235945 #
CHUNK_SIZE = 5000 

def analyze_claim(img_url):
    # (Existing AI judgment logic here...)
    pass

def solve_it():
    print(f"--- RUN #124: FINAL SCAN FROM BIRTH TO LATEST ---")
    current_block = w3.eth.block_number
    target_topic = w3.to_hex(w3.to_bytes(REAL_ID).rjust(32, b'\0'))
    
    found_any = False
    # Scan from the exact moment of creation to now
    for i in range(BIRTH_BLOCK, current_block + 1, CHUNK_SIZE):
        end = min(i + CHUNK_SIZE, current_block)
        print(f"Searching blocks {i} to {end}...")
        try:
            logs = w3.eth.get_logs({
                "fromBlock": i,
                "toBlock": end,
                "address": w3.to_checksum_address(CA),
                "topics": [None, target_topic]
            })
            if logs:
                found_any = True
                print(f"[!] FOUND {len(logs)} CLAIMS in this chunk!")
                # Process images...
        except Exception as e:
            print(f"Chunk failed: {e}")

    if not found_any:
        print("[X] Still 0. This suggests the claims might be on a different ID entirely.")

if __name__ == "__main__":
    solve_it()
