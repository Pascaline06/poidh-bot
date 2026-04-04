import time
import json
import os
from web3 import Web3

# =========================
# CONFIG
# =========================
# Use the environment variable for your Alchemy Key
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
# Signature for ClaimCreated
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

CHUNK_SIZE = 1000
STATE_FILE = "state.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def load_last_block():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)["last_block"]
    except:
        return None

def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)

def run_bot():
    print("🤖 Starting bot run...", flush=True)
    if not w3.is_connected():
        print("❌ RPC connection failed", flush=True)
        return

    latest_block = w3.eth.block_number
    last_block = load_last_block()

    # Fallback if no state exists (Start near bounty creation)
    if last_block is None:
        last_block = 44222459 
        print(f"⚠️ No state found. Starting from {last_block}", flush=True)

    print(f"🔍 Scanning blocks {last_block} → {latest_block}", flush=True)

    # Bounty ID must be padded to 32 bytes for the topics filter
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)

    current_start = last_block
    total_matches = 0

    while current_start <= latest_block:
        current_end = min(current_start + CHUNK_SIZE, latest_block)
        print(f"➡️ Chunk: {current_start} → {current_end}", flush=True)

        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG, None, None, topic_id]
            })

            for log in logs:
                tx_hash = log["transactionHash"].hex()
                # Extract the submitter address from Topic 2
                claimer = "0x" + log['topics'][2].hex()[-40:]
                
                # DECODING THE DESCRIPTION
                try:
                    # Skip metadata padding to get the actual string
                    raw_hex = log['data'].hex()[130:] 
                    description = bytes.fromhex(raw_hex).decode('utf-8', errors='ignore').strip('\x00')
                except:
                    description = "[Could not decode text]"

                print(f"\n✅ CLAIM DETECTED")
                print(f"User: {claimer}")
                print(f"Description: {description}")
                print(f"Link: https://basescan.org/tx/{tx_hash}")

                total_matches += 1

        except Exception as e:
            print(f"⚠️ Error at {current_start}: {e}")
            time.sleep(2)

        save_last_block(current_end)
        current_start = current_end + 1

    print(f"\n✅ Scan complete. Total matches: {total_matches}")

if __name__ == "__main__":
    run_bot()
