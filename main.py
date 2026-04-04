import time
import json
import os
from web3 import Web3
from google import genai

# =========================
# CONFIG
# =========================
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 1122

STATE_FILE = "state.json"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
w3 = Web3(Web3.HTTPProvider(RPC_URL))

def load_last_block():
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return int(data["last_block"])
    except:
        return 44100000 

def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": int(block)}, f)

def analyze_claim(text_content):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash", 
            contents=f"Review this bounty submission: '{text_content}'. Is it a valid physical book proof? Answer VALID/INVALID with a brief reason."
        )
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {e}"

def run_bot():
    print("🔌 Initializing connection...", flush=True)
    if not w3.is_connected():
        print("❌ Could not connect to Alchemy.")
        return
    
    start_block = load_last_block()
    current_chain_block = w3.eth.block_number
    
    # Scan exactly 1,000 blocks. Small enough to never trigger a 400 error.
    end_block = min(start_block + 1000, current_chain_block)
    
    # FIX: Convert to Hex strings for Alchemy's Base nodes
    from_hex = Web3.to_hex(start_block)
    to_hex = Web3.to_hex(end_block)
    
    # FIX: Correct 32-byte hex for Bounty ID
    bounty_topic = "0x" + hex(BOUNTY_ID)[2:].zfill(64)

    print(f"📡 Scanning {start_block} to {end_block} (Hex: {from_hex} -> {to_hex})", flush=True)

    try:
        # FIX: Providing the full 4-topic structure expected by the contract
        logs = w3.eth.get_logs({
            "fromBlock": from_hex,
            "toBlock": to_hex,
            "address": w3.to_checksum_address(POIDH_CA),
            "topics": [EVENT_SIG, bounty_topic, None, None] 
        })

        for log in logs:
            tx_hash = log["transactionHash"].hex()
            # Claimer is Topic 3 (the 4th item)
            claimer = "0x" + log['topics'][3].hex()[-40:]
            
            try:
                # Decoding the description from the data field
                data = log['data'].hex()
                # Skip offset(64) + length(64)
                clean_hex = data[128:].split('0000')[0]
                desc = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore').strip()
            except:
                desc = "[Empty or undecodable description]"

            print(f"\n🎯 CLAIM DETECTED")
            print(f"Submitter: {claimer}")
            print(f"AI Verdict: {analyze_claim(desc)}")
            print(f"Basescan: https://basescan.org/tx/{tx_hash}")

        save_last_block(end_block + 1)
        print(f"✅ Run complete. Next start: {end_block + 1}")

    except Exception as e:
        # This will print the actual technical reason if it fails
        print(f"❌ LOG ERROR: {e}")

if __name__ == "__main__":
    run_bot()
