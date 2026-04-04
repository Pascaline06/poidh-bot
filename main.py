import time
from web3 import Web3

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

def run_auto_scan():
    if not w3.is_connected():
        print("Connection Failed")
        return
    
    # Get the ACTUAL current block from the network
    latest_block = w3.eth.block_number
    # Scan back ~24 hours (roughly 43,200 blocks on Base)
    start_block = latest_block - 50000 
    
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    
    print(f"--- AUTO-SCANNING FROM BLOCK {start_block} TO {latest_block} ---")

    # Use small chunks to avoid the "Payload Too Large" error you saw earlier
    chunk_size = 2000
    current_start = start_block

    while current_start < latest_block:
        current_end = min(current_start + chunk_size, latest_block)
        
        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG, None, None, topic_id]
            })

            for log in logs:
                print(f"\n[!] SUCCESS: Claim found in Block {log['blockNumber']}")
                print(f"TX: https://basescan.org/tx/{log['transactionHash'].hex()}")

        except Exception as e:
            print(f"Chunk error at {current_start}: {e}")
            time.sleep(1)

        current_start = current_end + 1

    print("\n--- SCAN FINISHED ---")

if __name__ == "__main__":
    run_auto_scan()
