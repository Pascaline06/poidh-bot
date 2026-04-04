import time
import json
import os
from web3 import Web3

# =========================
# CONFIG
# =========================
# Ensure ALCHEMY_KEY is in your GitHub Secrets!
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"

# UPDATED: Target bounty 1122
BOUNTY_ID = 1122

# Tiny chunks (100) and limited scan (1000) to stop Alchemy 400 errors
CHUNK_SIZE = 100 
STATE_FILE = "state.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def load_last_block():
    """Tells the bot where it left off by reading state.json."""
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data["last_block"]
    except:
        # Fallback if state.json is missing
        return 44222459 

def save_last_block(block):
    """Saves the bot's progress so it doesn't repeat old scans."""
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)

def run_bot():
    print("🔌 Connecting to Base Mainnet...", flush=True)
    if not w3.is_connected():
        print("❌ RPC connection failed. Check your ALCHEMY_KEY.")
        return
    
    last_block = load_last_block()
    current_chain_block = w3.eth.block_number
    
    # We scan a max of 1000 blocks per run to ensure stability
    target_end_block = min(last_block + 1000, current_chain_block)

    print(f"✅ Connected! Scanning {last_block} → {target_end_block}", flush=True)

    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    current_start = last_block
    total_matches = 0

    while current_start < target_end_block:
        current_end = min(current_start + CHUNK_SIZE, target_end_block)
        
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
                
                # Decoding submission text
                try:
                    raw_data = log['data'].hex()
                    clean_hex = raw_data[130:].split('0000')[0]
                    desc = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore').strip()
                except:
                    desc = "[Decoding error]"

                print(f"\n✨ NEW CLAIM DETECTED")
                print(f"Submitter: {claimer}")
                print(f"Message: {desc}")
                print(f"TX Link: https://basescan.org/tx/{tx_hash}")
                total_matches += 1

        except Exception as e:
            print(f"⚠️ Alchemy Error at {current_start}: {e}")
            time.sleep(1)

        current_start = current_end + 1
    
    # Save the new spot
    save_last_block(target_end_block)
    print(f"\n✅ Scan complete. Claims found: {total_matches}")

if __name__ == "__main__":
    run_bot()
