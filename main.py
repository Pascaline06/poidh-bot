import os
import requests
import base64
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# This is the contract where you found the Bounty 136 birth
CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"

def final_event_hunt():
    print("--- RUN #118: THE EVENT HUNTER ---")
    current = w3.eth.block_number
    # Scanning the last 10,000 blocks to find those 6 claims
    start = current - 10000 
    
    # Topic for 'ClaimCreated' event
    CLAIM_TOPIC = "0x3939634e062635a16f2043685e13d1112d8a4e101966a87752495b2a0c4f8087"
    
    try:
        logs = w3.eth.get_logs({
            "fromBlock": start,
            "toBlock": "latest",
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CLAIM_TOPIC]
        })

        if not logs:
            print("[X] Still no claims found. This contract is definitely not the one with the 6 claims.")
            return

        print(f"[!] SUCCESS! Found {len(logs)} total claims on this contract.")
        for log in logs:
            # The Bounty ID is usually in Topic 1
            b_id = int(log['topics'][1].hex(), 16)
            print(f"-> Claim found for Bounty ID: {b_id} in Block {log['blockNumber']}")
            
            if b_id == 136:
                print("   [TARGET ACQUIRED] Found a claim for 136. Processing...")
                # Extracting IPFS from raw data hex
                raw_data = bytes.fromhex(log['data'].hex()).decode('utf-8', 'ignore')
                print(f"   Data: {raw_data[:100]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_event_hunt()
