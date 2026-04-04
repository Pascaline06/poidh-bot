import time
import json
import os
from web3 import Web3
import google.generativeai as genai

# =========================
# CONFIG
# =========================
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 1122

CHUNK_SIZE = 100 
STATE_FILE = "state.json"

# AI Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ai_model = genai.GenerativeModel('gemini-1.5-flash')

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
    """Uses Gemini to check if the submission sounds like a real book."""
    prompt = f"A user submitted this for a 'Physical Book' bounty: '{text_content}'. Is this a valid-sounding proof? Reply VALID or INVALID with a 1-sentence reason."
    try:
        response = ai_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {e}"

def run_bot():
    print("🔌 Starting Bot & AI Evaluator...", flush=True)
    if not w3.is_connected():
        print("❌ Connection failed.")
        return
    
    last_block = load_last_block()
    current_chain_block = w3.eth.block_number
    
    # Fast Catch-up: Scan 5,000 blocks per run
    target_end_block = min(last_block + 5000, current_chain_block)

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
                
                try:
                    raw_data = log['data'].hex()
                    clean_hex = raw_data[130:].split('0000')[0]
                    desc = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore').strip()
                except:
                    desc = "[No description found]"

                print(f"\n✨ CLAIM DETECTED")
                print(f"Submitter: {claimer}")
                
                # Gemini Evaluation
                verdict = analyze_claim(desc)
                print(f"Message: {desc}")
                print(f"🤖 AI Verdict: {verdict}")
                print(f"Link: https://basescan.org/tx/{tx_hash}")
                total_matches += 1

        except Exception as e:
            print(f"⚠️ Alchemy Error: {e}")
            time.sleep(1)

        current_start = current_end + 1
    
    save_last_block(target_end_block)
    print(f"\n✅ Finished! Found and analyzed {total_matches} claims.")

if __name__ == "__main__":
    run_bot()
