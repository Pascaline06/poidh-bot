import os
import requests
import base64
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
TARGET_ID = 136
# Hex for 136 is 88; we search for it in the log data
TARGET_HEX = "88" 
START_BLOCK = 44229555 

def get_pure_image(img_url):
    """Downloads the actual photo from IPFS gateways."""
    cid = img_url.split("/ipfs/")[-1] if "/ipfs/" in img_url else img_url
    cid = cid.split("?")[0].strip()
    gateways = [f"https://poidh.xyz/api/ipfs/{cid}", f"https://gateway.pinata.cloud/ipfs/{cid}", f"https://ipfs.io/ipfs/{cid}"]
    for url in gateways:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200 and "image" in res.headers.get('Content-Type', '').lower():
                return res.content
        except: continue
    return None

def analyze_with_gemini(img_data):
    """AI Verdict Logic."""
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
        # Using the broad scan range that worked in Run #102
        print(f"Aggressive Scan: Blocks {START_BLOCK} to {current_block}...")
        
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR)
        })

        print(f"Found {len(logs)} total events. Searching for Bounty 136 claims...")

        processed = 0
        for log in logs:
            raw_data = log['data'].hex()
            topics_combined = "".join([t.hex() for t in log['topics']])
            
            # Check if this log mentions ID 136 (88) and has an image link (http)
            if (TARGET_HEX in topics_combined or TARGET_HEX in raw_data) and "68747470" in raw_data:
                processed += 1
                start_idx = raw_data.find("68747470")
                img_url = bytes.fromhex(raw_data[start_idx:]).decode('utf-8', 'ignore').strip('\x00')
                
                print(f"\n[!] ANALYZING B01 CLAIM #{processed}")
                img_bytes = get_pure_image(img_url)
                if img_bytes:
                    result = analyze_with_gemini(img_bytes)
                    ans = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'NO VERDICT')
                    print(f"[*] AI VERDICT: {ans.strip().upper()}")
                else:
                    print("[X] Could not download image.")

        print(f"\nScan complete. Processed {processed} claims.")
    except Exception as e: print(f"[X] Error: {e}")

if __name__ == "__main__":
    run_automated_review()
