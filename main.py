import os
import json
import requests
from web3 import Web3

# Config
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 1122
STATE_FILE = "state.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def load_block():
    try:
        with open(STATE_FILE, "r") as f:
            return int(json.load(f)["last_block"])
    except:
        # Starting block for recent activity
        return 44290000 

def save_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": int(block)}, f)

def run_bot():
    if not w3.is_connected():
        print("❌ RPC Connection failed")
        return

    start = load_block()
    current_chain = w3.eth.block_number
    
    # Alchemy often fails if the range > 2000 blocks. We'll do 1000.
    end = min(start + 1000, current_chain)
    
    print(f"📡 Scanning blocks {start} to {end}...")

    # BOUNTY_ID must be a 64-character hex string for the 'topics' filter
    bounty_topic = "0x" + hex(BOUNTY_ID)[2:].zfill(64)

    # All numbers MUST be Hex strings for the Alchemy Base endpoint
    params = {
        "fromBlock": hex(start),
        "toBlock": hex(end),
        "address": w3.to_checksum_address(POIDH_CA),
        "topics": [EVENT_SIG, bounty_topic]
    }

    try:
        logs = w3.eth.get_logs(params)
        print(f"🔎 Found {len(logs)} logs.")
        for log in logs:
            tx = log["transactionHash"].hex()
            print(f"✨ Claim found: https://basescan.org/tx/{tx}")
        
        save_block(end + 1)
        print(f"✅ Progress saved. Next run starts at: {end + 1}")
    except Exception as e:
        print(f"❌ Alchemy Error: {e}")
        # This will print the actual reason Alchemy is angry
        if hasattr(e, 'response'):
            print(f"Detailed Error: {e.response.text}")

if __name__ == "__main__":
    run_bot()
