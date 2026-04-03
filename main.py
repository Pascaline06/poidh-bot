import os
import requests
import base64
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"

# THE TARGET LIST
TARGET_IDS = [136, 705, 706] 
# Starting slightly earlier to catch the exact creation block
START_BLOCK = 44229000 

def get_pure_image(img_url):
    """Aggressive fetcher for POIDH IPFS files."""
    cid = img_url.split("/ipfs/")[-1] if "/ipfs/" in img_url else img_url
    cid = cid.split("?")[0].strip()
    
    gateways = [
        f"https://poidh.xyz/api/ipfs/{cid}", 
        f"https://gateway.pinata.cloud/ipfs/{cid}",
        f"https://ipfs.io/ipfs/{cid}",
        f"https://cloudflare-ipfs.com/ipfs/{cid}"
    ]
    
    for url in gateways:
        try:
            res = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            c_type = res.headers.get('Content-Type', '').lower()
            if res.status_code == 200 and "image" in c_type:
                return res.content
        except:
            continue
    return None

def analyze_with_gemini(img_url):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={API_KEY}"
    img_data = get_pure_image(img_url)
    if not img_data:
        return {"error": "Image file not found on any gateway."}

    try:
        img_b64 = base64.b64encode(img_data).decode('utf-8')
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Is a hand holding a book? Answer YES or NO."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                ]
            }]
        }
        res = requests.post(api_url, json=payload, timeout=30)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def run_automated_review():
    try:
        current_block = w3.eth.block_number
        # Extended the search window to be absolutely sure
        print(f"Scanning blocks {START_BLOCK} to {current_block}...")
        
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CLAIM_TOPIC]
        })

        if not logs:
            print("No bounty logs found in this range.")

        for log in logs:
            # Extract ID from Topic 1 (indexed)
            on_chain_id = int(log['topics'][1].hex(), 16)
            
            if on_chain_id in TARGET_IDS:
                print(f"\n[!] MATCH FOUND: ID {on_chain_id}")
                raw_data = log['data'].hex()
                if "68747470" in raw_data: 
                    start_idx = raw_data.find("68747470")
                    img_url = bytes.fromhex(raw_data[start_idx:]).decode('utf-8', 'ignore').strip('\x00')
                    
                    result = analyze_with_gemini(img_url)
                    if 'candidates' in result:
                        verdict = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"[*] AI VERDICT FOR ID {on_chain_id}: {verdict.strip().upper()}")
                    else:
                        print(f"[X] AI Failure: {result}")
        print("\nReview Finished.")
    except Exception as e:
        print(f"[X] Critical System Error: {e}")

if __name__ == "__main__":
    run_automated_review()
