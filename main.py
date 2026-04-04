import os
import requests
import base64
import re
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
TARGET_ID = 136
# The exact birth block we found in Run #112
START_BLOCK = 44235945 

def get_pure_image(blob):
    """Downloads the image from IPFS gateways."""
    matches = re.findall(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{55}|https?://[^\s<>"]+|ipfs://[^\s<>"]+)', blob)
    if not matches: return None, None
    cid = matches[0].split("/ipfs/")[-1].replace("ipfs://", "").split("?")[0].strip()
    
    for url in [f"https://poidh.xyz/api/ipfs/{cid}", f"https://gateway.pinata.cloud/ipfs/{cid}", f"https://ipfs.io/ipfs/{cid}"]:
        try:
            res = requests.get(url, timeout=20)
            if res.status_code == 200 and len(res.content) > 500:
                return res.content, matches[0]
        except: continue
    return None, None

def analyze_with_gemini(img_data):
    """Asks the AI the core question."""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    try:
        img_b64 = base64.b64encode(img_data).decode('utf-8')
        payload = {"contents": [{"parts": [{"text": "Is a human hand holding a book? Answer ONLY YES or NO."}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
        res = requests.post(api_url, json=payload, timeout=30)
        return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'ERROR')
    except: return "API ERROR"

def run_surgical_strike():
    current_block = w3.eth.block_number
    print(f"Surgical Strike: Scanning blocks {START_BLOCK} to {current_block} for Bounty {TARGET_ID}...")
    
    # We filter specifically for ClaimCreated and the ID 136
    target_topic = w3.to_hex(w3.to_bytes(TARGET_ID).rjust(32, b'\0'))
    try:
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": ["0x3939634e062635a16f2043685e13d1112d8a4e101966a87752495b2a0c4f8087", target_topic]
        })

        if not logs:
            print(f"No claims found yet for ID {TARGET_ID} since its creation.")
            return

        print(f"Found {len(logs)} claims! Processing images...")
        for log in logs:
            raw_data = bytes.fromhex(log['data'].hex()).decode('utf-8', 'ignore')
            img_bytes, path = get_pure_image(raw_data)
            
            if img_bytes:
                print(f"[*] Analyzing image from block {log['blockNumber']}...")
                verdict = analyze_with_gemini(img_bytes)
                print(f"[VERDICT] BOUNTY {TARGET_ID}: {verdict.strip().upper()}")
            else:
                print(f"[X] Found claim in block {log['blockNumber']} but image failed to download.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_surgical_strike()
