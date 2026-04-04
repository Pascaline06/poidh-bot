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
# The keccak-256 hash of 'ClaimCreated(uint256,uint256,address,string)'
CLAIM_EVENT_TOPIC = "0x3939634e062635a16f2043685e13d1112d8a4e101966a87752495b2a0c4f8087"

# We'll scan from 44,150,000 up to where we last scanned
SCAN_START = 44150000
SCAN_END = 44229555
CHUNK_SIZE = 5000 # Smaller chunks to avoid "Payload Too Large"

def get_pure_image(blob):
    matches = re.findall(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{55}|https?://[^\s<>"]+|ipfs://[^\s<>"]+)', blob)
    if not matches: return None, None
    cid = matches[0].split("/ipfs/")[-1].replace("ipfs://", "").split("?")[0].strip()
    
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
        payload = {"contents": [{"parts": [{"text": "Is a hand holding a book? YES or NO."}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
        res = requests.post(api_url, json=payload, timeout=25)
        return res.json()
    except: return {}

def run_surgical_scan():
    print(f"Targeting Bounty {TARGET_ID}. Scanning in {CHUNK_SIZE} block increments...")
    
    current = SCAN_START
    while current < SCAN_END:
        top = min(current + CHUNK_SIZE, SCAN_END)
        print(f"Checking range: {current} to {top}...")
        
        try:
            logs = w3.eth.get_logs({
                "fromBlock": current,
                "toBlock": top,
                "address": w3.to_checksum_address(CONTRACT_ADDR),
                "topics": [CLAIM_EVENT_TOPIC]
            })

            for log in logs:
                # The Bounty ID is usually in topics[1] for these events
                try:
                    bounty_id = int(log['topics'][1].hex(), 16)
                    if bounty_id == TARGET_ID:
                        print(f"\n[!] MATCH: Found Bounty {TARGET_ID} in block {log['blockNumber']}")
                        raw_data = bytes.fromhex(log['data'].hex()).decode('utf-8', 'ignore')
                        img_bytes, path = get_pure_image(raw_data)
                        
                        if img_bytes:
                            print(f"[*] Judging image: {path[:30]}...")
                            res = analyze_with_gemini(img_bytes)
                            verdict = res.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'NO DATA')
                            print(f"[*] AI VERDICT: {verdict.strip().upper()}")
                        else:
                            print("[X] Claim found, but image failed to download.")
                except: continue

        except Exception as e:
            print(f"Chunk failed: {e}")
        
        current = top

if __name__ == "__main__":
    run_surgical_scan()
