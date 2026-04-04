import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Every address from your "Contract Identifier" screenshot
CANDIDATE_CAS = [
    "0x792fB0d6f1B42e3CbE5c78B1D88F67D21e3A5475",
    "0x69262A2D7C92c074720823B654FE7E4Cdb749747",
    "0x1a90Cb21b770d170821C0EBF56ce6Ffb2942e5D4",
    "0xADF60b2A0D10D234F31Ad5B2258cD3a16d6ef41D",
    "0x04b6E65c27a0b8a4cAb789E7909fa70881FDf888",
    "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"
]

TARGET_ID = 136
# Birth block confirmed in Run #112
START_BLOCK = 44235945 

def scan_all_candidates():
    print(f"--- RUN #121: MULTI-CONTRACT SWEEP FOR ID {TARGET_ID} ---")
    target_topic = w3.to_hex(w3.to_bytes(TARGET_ID).rjust(32, b'\0'))
    
    for ca in CANDIDATE_CAS:
        print(f"\nChecking CA: {ca}...")
        try:
            logs = w3.eth.get_logs({
                "fromBlock": START_BLOCK,
                "toBlock": "latest",
                "address": w3.to_checksum_address(ca),
                "topics": [None, target_topic]
            })
            
            if logs:
                print(f"[!!!] SUCCESS: Found {len(logs)} claims for ID 136 on {ca}!")
                return # Stop once we find the right one
            else:
                print(f"  > No claims for 136 here.")
                
        except Exception as e:
            print(f"  > Error: {e}")

if __name__ == "__main__":
    scan_all_candidates()
