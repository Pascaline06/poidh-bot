import os
import requests
import base64
import re
from web3 import Web3

# --- THE CORRECT CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# UPDATED: This is the widely used POIDH Bounty Contract on Base
CORRECT_CONTRACT = "0xB50D064fde85392D66649fD04E85C93683fba2B3" 
TARGET_ID = 136

def get_pure_image(blob):
    matches = re.findall(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{55}|https?://[^\s<>"]+|ipfs://[^\s<>"]+)', blob)
    if not matches: return None, None
    cid = matches[0].split("/ipfs/")[-1].replace("ipfs://", "").split("?")[0].strip()
    
    # Fast gateways to avoid more waiting
    for url in [f"https://poidh.xyz/api/ipfs/{cid}", f"https://gateway.pinata.cloud/ipfs/{cid}"]:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200: return res.content, matches[0]
        except: continue
    return None, None

def analyze_with_gemini(img_data):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    try:
        img_b64 = base64.b64encode(img_data).decode('utf-8')
        payload = {"contents": [{"parts": [{"text": "Is a human hand holding a book? YES or NO."}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
        res = requests.post(api_url, json=payload, timeout=25)
        return res.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'ERROR')
    except: return "API ERROR"

def solve_the_problem():
    print(f"--- RUN #116: FINAL SCAN ON CORRECT CONTRACT ---")
    # We look back 200,000 blocks (~5 days) to ensure we cover the 6 claims
    current = w3.eth.block_number
    start = current - 200000 
    
    target_topic = w3.to_hex(w3.to_bytes(TARGET_ID).rjust(32, b'\0'))
    
    try:
        # Searching specifically for the ClaimCreated event on the correct contract
        logs = w3.eth.get_logs({
            "from_block": start,
            "to_block": current,
            "address": w3.to_checksum_address(CORRECT_CONTRACT),
            "topics": ["0x3939634e062635a16f2043685e13d1112d8a4e101966a87752495b2a0c4f8087", target_topic]
        })

        if not logs:
            print("[X] Still no claims found. This means either the ID is not 136 or the contract is still wrong.")
            return

        print(f"[!] Found {len(logs)} claims! Judging them now...")
        for log in logs:
            raw_text = bytes.fromhex(log['data'].hex()).decode('utf-8', 'ignore')
            img_bytes, path = get_pure_image(raw_text)
            if img_bytes:
                result = analyze_with_gemini(img_bytes)
                print(f"[*] Block {log['blockNumber']} Verdict: {result.strip()}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_the_problem()
