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
# We are moving back 50k blocks to find this older bounty
DEEP_START_BLOCK = 44180000 

def get_pure_image(blob):
    """Smarter image extractor with longer timeouts for slow gateways."""
    matches = re.findall(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{55}|https?://[^\s<>"]+|ipfs://[^\s<>"]+)', blob)
    if not matches: return None, None
    
    path = matches[0]
    cid = path.split("/ipfs/")[-1] if "/ipfs/" in path else path
    cid = cid.replace("ipfs://", "").split("?")[0].strip()
    
    gateways = [
        f"https://poidh.xyz/api/ipfs/{cid}", 
        f"https://gateway.pinata.cloud/ipfs/{cid}", 
        f"https://ipfs.io/ipfs/{cid}",
        f"https://cloudflare-ipfs.com/ipfs/{cid}"
    ]
    for url in gateways:
        try:
            # Increased timeout to 20s to prevent 'Gateway Failed' errors
            res = requests.get(url, timeout=20) 
            if res.status_code == 200 and len(res.content) > 1000:
                return res.content, path
        except: continue
    return None, None

def analyze_with_gemini(img_data):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    try:
        img_b64 = base64.b64encode(img_data).decode('utf-8')
        payload = {"contents": [{"parts": [{"text": "Is a hand holding a book? YES or NO."}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
        res = requests.post(api_url, json=payload, timeout=30)
        return res.json()
    except Exception as e: return {"error": str(e)}

def run_deep_discovery():
    try:
        current_block = w3.eth.block_number
        print(f"Deep Scan: Blocks {DEEP_START_BLOCK} to {current_block}")
        
        logs = w3.eth.get_logs({
            "fromBlock": DEEP_START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR)
        })

        print(f"Total events found: {len(logs)}. Searching for ID {TARGET_ID}...")
        found_count = 0
        
        for log in logs:
            raw_data = log['data'].hex()
            # Convert the first topic to an integer to see the Bounty ID
            # Usually the ID is in the second or third topic (index 1 or 2)
            found_ids = []
            for t in log['topics']:
                try: found_ids.append(int(t.hex(), 16))
                except: pass
            
            # If our target 136 is in the topics, process it!
            if TARGET_ID in found_ids:
                found_count += 1
                print(f"\n[!] MATCH FOUND: Bounty {TARGET_ID} in Block {log['blockNumber']}")
                
                decoded = bytes.fromhex(raw_data).decode('utf-8', 'ignore')
                img_bytes, path = get_pure_image(decoded + raw_data)
                
                if img_bytes:
                    print(f"[*] Analyzing image: {path[:30]}...")
                    result = analyze_with_gemini(img_bytes)
                    ans = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'ERROR')
                    print(f"[*] RESULT: {ans.strip().upper()}")
                else:
                    print("[X] Could not download image for this claim.")

        if found_count == 0:
            print("\n[?] Still no 136. It might be even older or under a different contract.")
            # Print the IDs we DID find so we know what's happening
            sample_ids = set()
            for log in logs[:10]:
                for t in log['topics']:
                    try: sample_ids.add(int(t.hex(), 16))
                    except: pass
            print(f"Sample IDs found in this range: {list(sample_ids)[:5]}")

    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    run_deep_discovery()
