import time
import json
import os
from web3 import Web3

# =========================
# CONFIG
# =========================
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
# Event signature for ClaimCreated
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

CHUNK_SIZE = 500 
STATE_FILE = "state.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def load_last_block():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)["last_block"]
    except:
        # Start scanning near the block where bounty 136 was created
        return 44222459 

def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)

def run_bot():
    print("🔌 Testing RPC Connection...", flush=True)
    if not w3.is_connected():
        print("❌ RPC connection failed", flush=True)
        return
    
    latest_block = w3.eth.block_number
    last_block = load_last_block()
    
    # Safety: Limit the scan range per run to avoid Alchemy timeouts
    if latest_block - last_block > 2000:
        latest_block = last_block + 2000

    print(f"✅ Connected! Scanning {last_block} → {latest_block}", flush=True)

    # Pad Bounty ID to 32 bytes for the topic filter
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    current_start = last_block
    total_matches = 0

    while current_start < latest_block:
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
                
                # Decoding the 'description' string from the data field
                try:
                    raw_data = log['data'].hex()
                    # Skip metadata padding (130 hex chars) to find the text
                    clean_hex = raw_data[130:].split('0000')[0]
                    desc = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore').strip()
                except:
                    desc = "[Text hidden in hex]"

                print(f"\n✅ CLAIM DETECTED")
                print(f"Submitter: {claimer}")
                print(f"Submission Text: {desc}")
                print(f"Basescan: https://basescan.org/tx/{tx_hash}")
                total_matches += 1

        except Exception as e:
            print(f"⚠️ Alchemy Error at {current_start}: {e}")
            time.sleep(1)

        current_start = current_end + 1
    
    # Save progress so the next run starts where this one finished
    save_last_block(latest_block)
    print(f"\n✅ Run complete. New claims found: {total_matches}")

if __name__ == "__main__":
    run_bot()
