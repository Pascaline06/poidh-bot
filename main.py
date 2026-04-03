import os
import requests
import base64
from web3 import Web3

# --- CONFIGURATION ---
# These must be set as Secrets in your GitHub Repository
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Verified contract address and topic for POIDH bounties
CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"

# Updated to include your specific bounty ID 136
TARGET_IDS = [136, 705, 706] 
START_BLOCK = 44225000 

def get_pure_image(img_url):
    """Attempts to find raw image bytes using multiple gateways including POIDH's native API."""
    cid = img_url.split("/ipfs/")[-1] if "/ipfs/" in img_url else img_url
    cid = cid.split("?")[0].strip()
    
    # Prioritizing the POIDH native gateway and Pinata for reliability
    gateways = [
        f"https://poidh.xyz/api/ipfs/{cid}", 
        f"https://gateway.pinata.cloud/ipfs/{cid}",
        f"https://ipfs.io/ipfs/{cid}",
        f"https://{cid}.ipfs.nftstorage.link",
        f"https://cloudflare-ipfs.com/ipfs/{cid}"
    ]
    
    for url in gateways:
        try:
            print(f"[*] Attempting to fetch from: {url[:45]}...")
            res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            content_type = res.headers.get('Content-Type', '').lower()
            
            # Check for 200 OK, image content-type, and a minimum file size (2KB)
            if res.status_code == 200 and "image" in content_type and len(res.content) > 2000:
                print(f"[+] Successfully retrieved image ({len(res.content)} bytes)")
                return res.content
        except:
            continue
    return None

def analyze_with_gemini(img_url):
    """Encodes the image and sends it to Gemini for a YES/NO verdict."""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={API_KEY}"
    
    img_data = get_pure_image(img_url)
    if not img_data:
        return {"error": "Image data could not be retrieved from any gateway."}

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
    """Main loop: Scans blockchain logs and triggers AI for matching IDs."""
    try:
        current_block = w3.eth.block_number
        print(f"Scanning blocks {START_BLOCK} to {current_block} for IDs {TARGET_IDS}...")
        
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CLAIM_TOPIC]
        })

        for log in logs:
            on_chain_id = int(log['topics'][1].hex(), 16)
            
            if on_chain_id in TARGET_IDS:
                raw_data = log['data'].hex()
                # Find the hex start for 'http' to extract the image URL
                if "68747470" in raw_data: 
                    start_idx = raw_data.find("68747470")
                    img_url = bytes.fromhex(raw_data[start_idx:]).decode('utf-8', 'ignore').strip('\x00')
                    
                    print(f"\n[!] PROCESSING BOUNTY ID: {on_chain_id}")
                    result = analyze_with_gemini(img_url)
                    
                    if 'candidates' in result:
                        verdict = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"[*] AI VERDICT FOR ID {on_chain_id}: {verdict.strip().upper()}")
                    else:
                        print(f"[X] AI failed for ID {on_chain_id}: {result}")
        
        print("\nScan complete.")

    except Exception as e:
        print(f"[X] Critical Error: {e}")

if __name__ == "__main__":
    run_automated_review()
