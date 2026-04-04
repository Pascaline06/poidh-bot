import os
import requests
import base64
import re
from web3 import Web3

# --- THE CORRECTED CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# THE REAL POIDH CONTRACT IDENTIFIED IN RUN #119
REAL_CONTRACT = "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"
TARGET_ID = 136
# Start from the birth block found in Run #112
START_BLOCK = 44235945 

def get_pure_image(blob):
    matches = re.findall(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{55}|https?://[^\s<>"]+|ipfs://[^\s<>"]+)', blob)
    if not matches: return None
    cid = matches[0].split("/ipfs/")[-1].replace("ipfs://", "").split("?")[0].strip()
    # Fast gateway check
    try:
        res = requests.get(f"https://poidh.xyz/api/ipfs/{cid}", timeout=10)
        return res.content if res.status_code == 200 else None
    except: return None

def analyze_claim(img_data):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    img_b64 = base64.b64encode(img_data).decode('utf-8')
    payload = {"contents": [{"parts": [{"text": "Is a human hand holding a physical book? Answer ONLY YES or NO."}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
    try:
        res = requests.post(url, json=payload, timeout=20).json()
        return res['candidates'][0]['content']['parts'][0]['text'].strip()
    except: return "SCAN ERROR"

def run_final_judgment():
    print(f"--- RUN #120: JUDGING BOUNTY {TARGET_ID} ---")
    current_block = w3.eth.block_number
    target_topic = w3.to_hex(w3.to_bytes(TARGET_ID).rjust(32, b'\0'))
    
    # Scanning in chunks to avoid the 413 "Payload Too Large" error
    try:
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(REAL_CONTRACT),
            "topics": [None, target_topic] # Filter specifically for Bounty 136
        })

        if not logs:
            print("[!] No claims found. Double-check if 136 is the correct ID on this contract.")
            return

        print(f"[!] FOUND {len(logs)} CLAIMS. STARTING AI JUDGMENT...")
        for i, log in enumerate(logs, 1):
            raw_data = bytes.fromhex(log['data'].hex()).decode('utf-8', 'ignore')
            img_bytes = get_pure_image(raw_data)
            
            if img_bytes:
                verdict = analyze_claim(img_bytes)
                print(f"Claim {i} (Block {log['blockNumber']}): {verdict}")
            else:
                print(f"Claim {i}: Could not retrieve image from IPFS.")

    except Exception as e:
        print(f"Judgment Failed: {e}")

if __name__ == "__main__":
    run_final_judgment()
