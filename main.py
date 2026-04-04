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
# Event: ClaimCreated(uint256 indexed bountyId, uint256 indexed claimId, address indexed claimer, string description)
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 1122

STATE_FILE = "state.json"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
w3 = Web3(Web3.HTTPProvider(RPC_URL))

def load_last_block():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)["last_block"]
    except:
        return 44100000 

def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)

def analyze_claim(text_content):
    prompt = f"A user submitted this for a 'Physical Book' bounty: '{text_content}'. Is this a valid-sounding proof? Reply VALID or INVALID with a 1-sentence reason."
    try:
        response = client.models.generate_content(model="gemini-3-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {e}"

def run_bot():
    print("🔌 Starting Bot...", flush=True)
    if not w3.is_connected():
        print("❌ RPC Connection Failed.")
        return
    
    last_block = load_last_block()
    current_block = w3.eth.block_number
    
    # We scan in small, healthy chunks of 1000 blocks to avoid Alchemy 400s
    scan_end = min(last_block + 1000, current_block)
    
    # FORMATTING FIX: Convert integers to Hex strings for the RPC request
    from_hex = hex(last_block)
    to_hex = hex(scan_end)
    
    # TOPIC FIX: Ensure the Bounty ID is in the FIRST indexed slot (Topic 1)
    bounty_topic = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    
    print(f"📡 Scanning Blocks {last_block} to {scan_end}...", flush=True)

    try:
        logs = w3.eth.get_logs({
            "fromBlock": from_hex,
            "toBlock": to_hex,
            "address": w3.to_checksum_address(POIDH_CA),
            "topics": [EVENT_SIG, bounty_topic] # Filter: [Signature, BountyID]
        })

        for log in logs:
            tx_hash = log["transactionHash"].hex()
            # Claimer is the 3rd indexed parameter (Topic 3)
            claimer = "0x" + log['topics'][3].hex()[-40:]
            
            # Data contains the non-indexed string (Description)
            try:
                # Basic string decoding from EVM data
                raw_data = log['data'].hex()
                # Skip the first 128 chars (offset + length markers)
                clean_hex = raw_data[128:].split('0000')[0] 
                desc = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore').strip()
            except:
                desc = "Could not decode description"

            print(f"\n✨ CLAIM DETECTED")
            print(f"From: {claimer}")
            print(f"🤖 AI Verdict: {analyze_claim(desc)}")
            print(f"Link: https://basescan.org/tx/{tx_hash}")

        save_last_block(scan_end + 1)
        print(f"✅ Chunk finished. Next scan starts at {scan_end + 1}")

    except Exception as e:
        # This will print the EXACT error from Alchemy so we can see the 'real' problem
        print(f"❌ RPC ERROR: {str(e)}")

if __name__ == "__main__":
    run_bot()
