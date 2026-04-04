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
TARGET_ID_HEX = "88" # Hex for 136
START_BLOCK = 44229555 

def get_pure_image(blob):
    """Uses regex to find IPFS CIDs or URLs anywhere in the log data."""
    # Matches Qm... or bafy... CIDs and standard http/ipfs links
    matches = re.findall(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{55}|https?://[^\s<>"]+|ipfs://[^\s<>"]+)', blob)
    if not matches: return None, None
    
    path = matches[0]
    cid = path.split("/ipfs/")[-1] if "/ipfs/" in path else path
    cid = cid.replace("ipfs://", "").split("?")[0].strip()
    
    # Try the most reliable gateways first
    gateways = [
        f"https://poidh.xyz/api/ipfs/{cid}", 
        f"https://gateway.pinata.cloud/ipfs/{cid}", 
        f"https://ipfs.io/ipfs/{cid}"
    ]
    for url in gateways:
        try:
            res = requests.get(url, timeout=12)
            if res.status_code == 200:
                return res.content, path
        except: continue
    return None, None

def analyze_with_gemini(img_data):
    """The AI Judge logic."""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={API_KEY}"
    try:
        img_b64 = base64.b64encode(img_data).decode('utf-8')
        payload = {"contents": [{"parts": [{"text": "Is a hand holding a book? Answer YES or NO."}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
        res = requests.post(api_url, json=payload, timeout=20)
        return res.json()
    except Exception as e: return {"error": str(e)}

def run_automated_review():
    try:
        current_block = w3.eth.block_number
        print(f"B01 Recovery: Scanning blocks {START_BLOCK} to {current_block}...")
        
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR)
        })

        print(f"Found {len(logs)} contract events. Hunting for Bounty 136 claims...")
        processed = 0
        
        for log in logs:
            # Combine all data from topics and the data field for a 'fuzzy' search
            raw_data = log['data'].hex()
            topics_combined = "".join([t.hex() for t in log['topics']])
            all_hex = (topics_combined + raw_data).lower()
            
            # If the bounty ID 136 (hex 88) is found anywhere in this event
            if TARGET_ID_HEX in all_hex:
                # Decode the raw data to look for the claim's image link
                decoded = bytes.fromhex(raw_data).decode('utf-8', 'ignore')
                img_bytes, found_path = get_pure_image(decoded + raw_data)
                
                if img_bytes:
                    processed += 1
                    print(f"\n[!] ANALYZING B01 CLAIM #{processed}")
                    print(f"[*] Found: {found_path[:40]}...")
                    
                    result = analyze_with_gemini(img_bytes)
                    ans = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'NO VERDICT')
                    print(f"[*] AI VERDICT: {ans.strip().upper()}")

        print(f"\nScan complete. Successfully judged {processed} claims.")
    except Exception as e: print(f"[X] Critical Failure: {e}")

if __name__ == "__main__":
    run_automated_review()
