import os
from web3 import Web3

# Using a public RPC, but a private Alchemy/QuickNode key is better for 429 errors
RPC_URL = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# CONTRACT DATA FROM YOUR LOGS
TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
# This is the hash for ClaimCreated(uint256,address,uint256,address,string,string,uint256,string,uint256)
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
REAL_ID = 136 
# Start earlier than the birth block to ensure no claims are missed
START_BLOCK = 44230000 

def final_attempt():
    print(f"--- RUN #134: THE ABSOLUTE FINAL SCAN FOR ID {REAL_ID} ---")
    
    # Correctly pad the ID to 32 bytes (64 hex chars)
    topic_id = "0x" + hex(REAL_ID)[2:].zfill(64)
    
    # We use None for topics 1 and 2 to catch any issuer/claimant
    # and put our target ID in the Topic 3 slot as seen in your log
    filter_params = {
        "fromBlock": START_BLOCK,
        "toBlock": "latest",
        "address": w3.to_checksum_address(TARGET_CA),
        "topics": [EVENT_SIG, None, None, topic_id]
    }

    try:
        logs = w3.eth.get_logs(filter_params)
        
        if not logs:
            print(f"Still 0. This implies the claims are on a different contract version.")
        else:
            print(f"FINALLY! Found {len(logs)} claims.")
            for log in logs:
                print(f"TX: https://basescan.org/tx/{log['transactionHash'].hex()}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_attempt()
