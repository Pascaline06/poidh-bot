import time
from web3 import Web3

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# THE POIDH CONTRACT (Verified from your logs)
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

# 2. THE REAL BLOCK RANGE (Based on your screenshot 032923)
# Your TX was in block 14,099,451. We scan a small window around it.
START_BLOCK = 14099000 
END_BLOCK = 14105000 

def run_bot():
    if not w3.is_connected(): return
    
    # Format ID 136 to 32-byte hex
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    
    print(f"--- RUNNING ACCURATE SCAN FOR BOUNTY {BOUNTY_ID} ---")
    print(f"Scanning range: {START_BLOCK} to {END_BLOCK}")

    try:
        # THE FIX: Place bountyId in Topic 3 (Index 3)
        # Structure: [Event, Topic1, Topic2, Topic3]
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": END_BLOCK,
            "address": w3.to_checksum_address(POIDH_CA),
            "topics": [EVENT_SIG, None, None, topic_id]
        })

        if not logs:
            print("No claims found in this range.")
        else:
            for log in logs:
                tx = log['transactionHash'].hex()
                print(f"\n[!] CLAIM FOUND!")
                print(f"Block: {log['blockNumber']}")
                print(f"TX: https://basescan.org/tx/{tx}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_bot()
