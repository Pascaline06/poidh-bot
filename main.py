import time
import json
import os
from web3 import Web3
from google import genai  # Upgraded to the new 2026 SDK

# =========================
# CONFIG
# =========================
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 1122

CHUNK_SIZE = 1000 
STATE_FILE = "state.json"

# New AI Setup (Gemini 3 Flash)
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
    """Uses Gemini 3 Flash to check if the submission sounds like a real book."""
    prompt = f"A user submitted this for a 'Physical Book' bounty: '{text_content}'. Is this a valid-sounding proof? Reply VALID or INVALID with a 1-sentence reason."
    try:
        # Using the updated 2026 model call
        response = client.models.generate_content(
            model="gemini-3-flash", 
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {e}"

def run_bot():
    print("🔌 Starting Bot & Gemini 3 Evaluator...", flush=True)
    if not w3.is_connected():
        print("❌ Connection failed.")
        return
    
    last_block = load_last_block()
    current_chain_block = w3.eth.block_number
    
    # Scan 5,000 blocks per run to catch those 6 claims from yesterday
    target_end_block = min(last_block + 5000, current_chain_block)

    print(f"✅ Connected! Scanning {last_block} → {target_end_block}", flush=True)

    # Convert ID to 32-byte hex
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)
    
    # FIX: BountyID is Topic 1, not Topic 3!
    filter_topics = [EVENT_SIG, topic_id, None, None]

    current_start = last_block
    total_matches = 0

    while current_start < target_end_block:
        current_end = min(current_start + CHUNK_SIZE, target_end_block)
        
        try:
            logs = w3.eth.get_logs({
                "fromBlock": hex(current_start), # Using Hex to please Alchemy
                "toBlock": hex(current_end),
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": filter_topics
            })

            for log in logs:
                tx_hash = log["transactionHash"].hex()
                # The claimer is in Topic 3
                claimer = "0x" + log['topics'][3].hex()[-40:]
                
                # Robust decoding of the description string
                try:
                    data_hex = log['data'].hex()
                    # Strings start after the 64-char offset and 64-char length
                    desc_hex = data_hex[128:]
                    desc = bytes.fromhex(desc_hex).decode('utf-8', errors='ignore').split('\x00')[0].strip()
                except:
                    desc = "[No description found]"

                print(f"\n✨ CLAIM DETECTED")
                print(f"Submitter: {claimer}")
                
                verdict = analyze_claim(desc)
                print(f"Message: {desc}")
                print(f"🤖 AI Verdict: {verdict}")
                print(f"Link: https://basescan.org/tx/{tx_hash}")
                total_matches += 1

        except Exception as e:
            print(f"⚠️ Alchemy/RPC Error: {e}")
            time.sleep(1)

        current_start = current_end + 1
    
    save_last_block(target_end_block)
    print(f"\n✅ Finished! Found and analyzed {total_matches} claims.")

if __name__ == "__main__":
    run_bot()
