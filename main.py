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
TARGET_IDS = [136, 705, 706] 
START_BLOCK = 44225000 

def get_pure_image(img_url):
    """Bypasses 'loading' pages to find the raw image data."""
    cid = img_url.split("/ipfs/")[-1] if "/ipfs/" in img_url else img_url
    # prioritizing gateways that often serve raw data directly
    gateways = [
        f"https://{cid}.ipfs.nftstorage.link",
        f"https://ipfs.io/ipfs/{cid}",
        f"https://cloudflare-ipfs.com/ipfs/{cid}"
    ]
    
    for url in gateways:
        try:
            res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            # CRITICAL: Verify this is actually an image (JPEG, PNG, etc)
            content_type = res.headers.get('Content-Type', '')
            if res.status_code == 200 and "image" in content_type:
                return res.content
        except:
            continue
    return None

def analyze_with_gemini(img_url):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={API_KEY}"
    
    img_data = get_pure_image(img_url)
    if not img_data:
        return {"error": "Could not find a raw image file at any gateway."}

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
        print(f"Scanning from {START_BLOCK} for IDs {TARGET_IDS}...")
        
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
                if "68747470" in raw_data: 
                    start_index = raw_data.find("68747470")
                    img_url = bytes.fromhex(raw_data[start_index:]).decode('utf-8', 'ignore').strip('\x00')
                    print(f"\n[!] VALIDATING ID {on_chain_id}...")
                    
                    result = analyze_with_gemini(img_url)
                    if 'candidates' in result:
                        answer = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"[*] AI VERDICT: {answer.strip()}")
                    else:
                        print(f"[X] AI Failure: {result}")
    except Exception as e:
        print(f"[X] System Error: {e}")

if __name__ == "__main__":
    run_automated_review()
