import time
import json
import os
from web3 import Web3

# =========================
# CONFIG
# =========================
# Ensure your Alchemy key is in GitHub Secrets!
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

CHUNK_SIZE = 1000 # Stable size for Alchemy
STATE_FILE = "state.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def load_last_block():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)["last_block"]
    except:
        return 44222459 # Start from bounty creation

def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)

def run_bot():
    print("🤖 Starting bot run...", flush=True)
    if not w3.is_connected():
        print("❌ RPC connection failed")
        return

    latest_block = w3.eth.block_number
    last_block = load_last_block()
    
    # Safety: don't scan too far back if state is lost
    if latest_block - last_block > 5000:
        last_block = latest_block - 5000

    print(f"🔍 Scanning {last_block} → {latest_block}", flush=True)

    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    current_start = last_block
    total_matches = 0

    while current_start <= latest_block:
        current_end = min(current_start + CHUNK_SIZE, latest_block)
        
        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG, None, None, topic_id]
            })

            for log in logs:
                tx_hash = log["transactionHash"].hex()
                claimer = "0x" + log['topics'][2].hex()[-40:]
                
                # Decoding the description from hex
                try:
                    raw_hex = log['data'].hex()[130:] 
                    desc = bytes.fromhex(raw_hex).decode('utf-8', errors='ignore').strip('\x00')
                except:
                    desc = "[Decoding Error]"

                print(f"\n✅ CLAIM FOUND")
                print(f"User: {claimer}")
                print(f"Description: {desc}")
                print(f"TX: https://basescan.org/tx/{tx_hash}")
                total_matches += 1

        except Exception as e:
            print(f"⚠️ RPC Error at {current_start}: {e}")
            time.sleep(1) # Short wait for rate limits

        current_start = current_end + 1
    
    # Save the absolute latest block scanned
    save_last_block(latest_block)
    print(f"\n✅ Finished. Total matches: {total_matches}")

if __name__ == "__main__":
    run_bot()
