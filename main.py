import os
import json
import time
from web3 import Web3

# Configuration
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 1122
STATE_FILE = "state.json"
# Reduced range to avoid Alchemy 400 errors
BLOCK_STEP = 500 

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def get_last_block():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("last_block", 44100000)
    except FileNotFoundError:
        return 44100000

def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)

def run_bot():
    if not os.getenv('ALCHEMY_KEY'):
        print("❌ ERROR: ALCHEMY_KEY is missing from environment secrets!")
        return

    from_block = get_last_block()
    latest_block = w3.eth.block_number
    to_block = min(from_block + BLOCK_STEP, latest_block)

    if from_block >= latest_block:
        print("✅ Already at the tip of the chain.")
        return

    print(f"📡 Scanning {from_block} to {to_block}...")

    # Precise filter to avoid 400 errors
    EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
    bounty_topic = "0x" + hex(BOUNTY_ID)[2:].zfill(64)

    try:
        logs = w3.eth.get_logs({
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
            "address": Web3.to_checksum_address(POIDH_CA),
            "topics": [EVENT_SIG, bounty_topic] # Clean topics list
        })

        for log in logs:
            print(f"🎉 New Claim Found in block {log['blockNumber']}!")
            # Add your notification logic (Farcaster/Telegram) here

        save_last_block(to_block)
        print(f"💾 Progress saved: {to_block}")

    except Exception as e:
        print(f"❌ RPC ERROR: {e}")

if __name__ == "__main__":
    run_bot()
