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
# The exact 32-byte hex for 136 (88)
TARGET_HEX_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000088"
START_BLOCK = 44229555 

def get_pure_image(cid_or_url):
    """Turns raw CID or URL into an image."""
    cid = cid_or_url.split("/ipfs/")[-1] if "/ipfs/" in cid_or_url else cid_or_url
    cid = cid.replace("ipfs://", "").split("?")[0].strip()
    
    # We try gateways with the raw CID directly
    gateways = [
        f"https://poidh.xyz/api/ipfs/{cid}", 
        f"https://gateway.pinata.cloud/ipfs/{cid}", 
        f"https://ipfs.io/ipfs/{cid}"
    ]
    for url in gateways:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200 and "image" in res.headers.get('Content-Type', '').lower():
                return res.content
        except: continue
    return None

def analyze_with_gemini(img_data):
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
        print(f"B01 Final Sweep: Blocks {START_BLOCK} to {current_block}...")
        
        logs = w3.eth.get_logs({
            "from_block": START_BLOCK,
            "to_block": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR)
        })

        processed = 0
        for log in logs:
            # Look for ID 136 in the indexed topics (where IDs usually live)
            is_bounty_136 = any(TARGET_HEX_TOPIC.lower() == t.hex().lower() for t in log['topics'])
            
            if is_bounty_136:
                processed += 1
                raw_data = log['data'].hex()
                
                # Attempt to extract CID from the raw data
                # If there's no 'http', we assume the whole data string might be a CID
                try:
                    if "68747470" in raw_data:
                        start_idx = raw_data.find("68747470")
                        cid_or_url = bytes.fromhex(raw_data[start_idx:]).decode('utf-8', 'ignore').strip('\x00')
                    else:
                        # Fallback: decode the whole data block to find a CID string
                        cid_or_url = bytes.fromhex(raw_data).decode('utf-8', 'ignore').strip('\x00').strip()
                    
                    if not cid_or_url: continue

                    print(f"\n[!] ANALYZING B01 CLAIM #{processed}")
                    img_bytes = get_pure_image(cid_or_url)
                    
                    if img_bytes:
                        result = analyze_with_gemini(img_bytes)
                        ans = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'NO VERDICT')
                        print(f"[*] AI VERDICT: {ans.strip().upper()}")
                    else:
                        print(f"[X] Could not resolve image for: {cid_or_url[:20]}...")
                except:
                    continue

        print(f"\nScan complete. Processed {processed} claims.")
    except Exception as e: print(f"[X] Error: {e}")

if __name__ == "__main__":
    run_automated_review()
