import time
import json
import os
import requests
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
        return 44222459 

def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)

def analyze_submission(text_content):
    """Uses Gemini 1.5 Flash to evaluate the claim text/image."""
    prompt = f"""
    The user is claiming a bounty for 'Holding a Physical Book'. 
    Submission description: "{text_content}"
    
    Is this a valid-sounding submission for a physical book? 
    Reply with 'VALID' or 'INVALID' and a short reason.
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {e}"

def run_bot():
    print("🔌 Connecting and initializing AI...", flush=True)
    if not w3.is_connected():
        print("❌ RPC connection failed.")
        return
    
    last_block = load_last_block()
    current_chain_block = w3.eth.block_number
    target_end_block = min(last_block + 1000, current_chain_block)

    print(f"✅ Scanning {last_block} → {target_end_block}", flush=True)

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
                
                # Decode submission text
                try:
                    raw_data = log['data'].hex()
                    clean_hex = raw_data[130:].split('0000')[0]
                    desc = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore').strip()
                except:
                    desc = "[No text found]"

                print(f"\n🔍 EVALUATING CLAIM: {claimer}")
                
                # CALL THE AI
                ai_verdict = analyze_submission(desc)
                
                print(f"Description: {desc}")
                print(f"AI Verdict: {ai_verdict}")
                print(f"TX: https://basescan.org/tx/{tx_hash}")
                total_matches += 1

        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(1)

        current_start = current_end + 1
    
    save_last_block(target_end_block)
    print(f"\n✅ Run complete. New claims analyzed: {total_matches}")

if __name__ == "__main__":
    run_bot()
