import time
from web3 import Web3

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

# 2. BLOCK RANGE (Covers all of yesterday and today)
START_BLOCK = 44100000 
END_BLOCK = 44260000
CHUNK_SIZE = 2000 

def run_deep_scan():
    if not w3.is_connected(): return
    
    # Format ID 136 for the blockchain
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    
    print(f"--- SCANNING FOR BOUNTY ID {BOUNTY_ID} (TOPIC 3 FIX) ---")
    
    current_start = START_BLOCK
    while current_start < END_BLOCK:
        current_end = min(current_start + CHUNK_SIZE, END_BLOCK)
        
        try:
            # THE FIX: Placing bountyId in the 4th position (index 3)
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG, None, None, topic_id]
            })

            for log in logs:
                print(f"\n[!] MATCH FOUND: Block {log['blockNumber']}")
                print(f"TX: https://basescan.org/tx/{log['transactionHash'].hex()}")

        except Exception as e:
            print(f"Error at {current_start}: {e}")
            time.sleep(1)

        current_start = current_end + 1

    print("\n--- SCAN FINISHED ---")

if __name__ == "__main__":
    run_deep_scan()
