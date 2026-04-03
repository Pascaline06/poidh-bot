import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# This is the "Topic" for a ClaimCreated event (standard across most bounty contracts)
CLAIM_TOPIC = "0x" + Web3.keccak(text="ClaimCreated(uint256,uint256,address,string)").hex()

def find_the_real_contract():
    print("🔎 Searching for the correct Bounty contract address...")
    try:
        current_block = w3.eth.block_number
        # Search the last 500 blocks for ANY ClaimCreated event
        logs = w3.eth.get_logs({
            "fromBlock": current_block - 500,
            "toBlock": current_block,
            "topics": [CLAIM_TOPIC]
        })

        if not logs:
            print("ℹ️ No claim events found in the last 500 blocks. Trying a wider scan...")
            logs = w3.eth.get_logs({
                "fromBlock": current_block - 2000,
                "toBlock": current_block,
                "topics": [CLAIM_TOPIC]
            })

        found_addresses = set()
        for log in logs:
            found_addresses.add(log['address'])
        
        if found_addresses:
            print(f"✅ FOUND {len(found_addresses)} POTENTIAL CONTRACT(S):")
            for addr in found_addresses:
                print(f"👉 {addr}")
            print("\nCompare these to the '0x5555...' address in your code. One of these is the winner.")
        else:
            print("❌ No Claim events found at all. The contract might use a different event name.")

    except Exception as e:
        print(f"❌ Error during hunt: {e}")

if __name__ == "__main__":
    find_the_real_contract()
