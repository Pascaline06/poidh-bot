import os
import requests
import base64
import re
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CORRECT_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
REAL_ID = 1122 
CHUNK_SIZE = 2000 # Small chunks to avoid 413 errors

def get_pure_image(blob):
    matches = re.findall(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{55})', blob)
    if not matches: return None
    cid = matches[0]
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

def run_chunked_scan():
    print(f"--- RUN #123: CHUNKED SCAN FOR ID {REAL_ID} ---")
    current_block = w3.eth.block_number
    # Scan the last 10,000 blocks in chunks
    start_block = current_block - 10000
    target_topic = w3.to_hex(w3.to_bytes(REAL_ID).rjust(32, b'\0'))
    
    all_logs = []
    for i in range(start_block, current_block, CHUNK_SIZE):
        end = min(i + CHUNK_SIZE, current_block)
        print(f"Scanning blocks {i} to {end}...")
        try:
            logs = w3.eth.get_logs({
                "fromBlock": i,
                "toBlock": end,
                "address": w3.to_checksum_address(CORRECT_CA),
                "topics": [None, target_topic]
            })
            all_logs.extend(logs)
        except Exception as e:
            print(f"Chunk failed: {e}")

    if not all_logs:
        print("[!] No claims found in the scanned range.")
        return

    print(f"[!] SUCCESS: Found {len(all_logs)} claims. Judging now...")
    for log in all_logs:
        raw_data = bytes.fromhex(log['data'].hex()).decode('utf-8', 'ignore')
        img_bytes = get_pure_image(raw_data)
        if img_bytes:
            print(f"Block {log['blockNumber']} Verdict: {analyze_claim(img_bytes)}")

if __name__ == "__main__":
    run_chunked_scan()
