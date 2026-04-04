import time
from web3 import Web3

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

# 2. THE CORRECT RANGE (Around the block from your screenshot)
# Block 44222459 was 20 hours ago. We scan around it.
START_BLOCK = 44220000 
END_BLOCK = 44230000 

def run_final_check():
    if not w3.is_connected(): return
    
    # Format ID 136 to 32-byte hex
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    
    print(f"--- SCANNING RANGE {START_BLOCK} TO {END_BLOCK} ---")

    try:
        # THE FIX: [Event Sig, Topic 1, Topic 2, Topic 3]
        # Topic 1 = id, Topic 2 = issuer, Topic 3 = bountyId
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": END_BLOCK,
            "address": w3.to_checksum_address(POIDH_CA),
            "topics": [EVENT_SIG, None, None, topic_id]
        })

        if not logs:
            print("No claims found. Trying slightly wider range...")
        else:
            for log in logs:
                tx = log['transactionHash'].hex()
                print(f"\n[!] SUCCESS: Claim Found in Block {log['blockNumber']}")
                print(f"TX: https://basescan.org/tx/{tx}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_final_check()
