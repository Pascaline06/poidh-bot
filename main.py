import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"

def debug_all_claims():
    print(f"🕵️ Extracting ALL claims from {CONTRACT_ADDR}...")
    try:
        current_block = w3.eth.block_number
        logs = w3.eth.get_logs({
            "fromBlock": current_block - 2000,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CLAIM_TOPIC]
        })

        if not logs:
            print("❌ No claims found at all. Check the contract address one more time.")
            return

        print(f"✅ FOUND {len(logs)} CLAIMS. Printing IDs and Data:")
        for i, log in enumerate(logs):
            bounty_id = int(log['topics'][1].hex(), 16)
            print(f"Claim {i+1}: Bounty ID {bounty_id} | Data: {log['data'].hex()[:50]}...")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_all_claims()
