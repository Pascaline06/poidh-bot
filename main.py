import os
import requests
import base64
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
# Targeted specifically to your B01 bounty
TARGET_IDS = [136] 
# Start 100 blocks before your transaction (44229655)
START_BLOCK = 44229555 

def get_pure_image(img_url):
    """Aggressively hunts for the raw photo of the book."""
    cid = img_url.split("/ipfs/")[-1] if "/ipfs/" in img_url else img_url
    cid = cid.split("?")[0].strip()
    
    gateways = [
        f"https://poidh.xyz/api/ipfs/{cid}", 
        f"https://gateway.pinata.cloud/ipfs/{cid}",
        f"https://ipfs.io/ipfs/{cid}"
    ]
    
    for url in gateways:
        try:
            res = requests.get(url, timeout=15)
            # Only accept real images, not 'Loading' HTML pages
            if res.status_code == 200 and "image" in res.headers.get('Content-Type', '').lower():
                return res.content
        except:
            continue
    return None

def analyze_with_gemini(img_data):
    """Sends the raw book photo to Gemini for judgment."""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={API_KEY}"
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
        res = requests.post(api_url, json=payload, timeout=20)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def run_automated_review():
    try:
        current_block = w3.eth.block_number
        print(f"B01 Search: Scanning blocks {START_BLOCK} to {current_block}...")
        
        # We search ALL contract events to ensure we don't miss the B01 creation
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR)
        })

        print(f"Found {len(logs)} potential events. Filtering for B01 (ID 136)...")

        for log in logs:
            raw_data = log['data'].hex()
            # Look for the URL inside the blockchain log
            if "68747470" in raw_data: 
                try:
                    # Extract ID (Topic 1 is usually the Bounty ID)
                    found_id = int(log['topics'][1].hex(), 16)
                except:
                    continue

                if found_id in TARGET_IDS:
                    print(f"\n[!] B01 BOUNTY DETECTED (ID {found_id})")
                    start_idx = raw_data.find("68747470")
                    img_url = bytes.fromhex(raw_data[start_idx:]).decode('utf-8', 'ignore').strip('\x00')
                    
                    img_bytes = get_pure_image(img_url)
                    if img_bytes:
                        result = analyze_with_gemini(img_bytes)
                        if 'candidates' in result:
                            ans = result['candidates'][0]['content']['parts'][0]['text']
                            print(f"[*] AI VERDICT FOR B01: {ans.strip().upper()}")
                        else:
                            print(f"[X] AI failed to judge: {result}")
                    else:
                        print("[X] Could not download the book photo.")
        
        print("\nScan Finished.")
    except Exception as e:
        print(f"[X] System Error: {e}")

if __name__ == "__main__":
    run_automated_review()
