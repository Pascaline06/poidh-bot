import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
TARGET_ID = 136

def find_bounty_block():
    print(f"Locating Bounty {TARGET_ID}...")
    # The event hash for BountyCreated
    CREATED_EVENT = "0x28976766440c4a4f899d45e4682022f465c4901f46f499d34850020138981442"
    
    # We scan a massive range because this is a very light search
    try:
        logs = w3.eth.get_logs({
            "fromBlock": 40000000, 
            "toBlock": "latest",
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CREATED_EVENT, w3.to_hex(w3.to_bytes(TARGET_ID).rjust(32, b'\0'))]
        })

        if logs:
            block = logs[0]['blockNumber']
            print(f"\n[!!!] FOUND IT: Bounty 136 was created in Block: {block}")
            print(f"Now we just need to scan block {block} to find the claims.")
        else:
            print("\n[?] Bounty 136 not found in this contract's history.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_bounty_block()
