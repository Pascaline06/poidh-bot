import os
import requests
import base64
from web3 import Web3

# --- CONFIG ---
# These must be set in your GitHub Secrets
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Contract constants from your logs
CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_IDS = [705, 706]

def analyze_with_gemini(img_url):
    """Sends image to Gemini 3.1 Flash Lite via the v1beta REST endpoint."""
    # Updated to v1beta and the specific 3.1 Lite model seen in your AI Studio
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={API_KEY}"
    
    try:
        # 1. Download image
        img_response = requests.get(img_url, timeout=10)
        img_response.raise_for_status()
        
        # 2. Encode to Base64 (Standard for Google API)
        img_b64 = base64.b64encode(img_response.content).decode('utf-8')
        
        # 3. Construct Payload
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Is a hand holding a book? Answer YES or NO."},
                    {"inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64
                    }}
                ]
            }]
        }
        
        # 4. API Request
        res = requests.post(url, json=payload, timeout=20)
        
        if res.status_code == 200:
            return res.json()
        else:
            return {"error": f"API Error {res.status_code}: {res.text}"}
            
    except Exception as e:
        return {"error": str(e)}

def run_automated_review():
    try:
        current_block = w3.eth.block_number
        print(f"Checking IDs {TARGET_IDS} near block {current_block}...")
        
        # Search last 10,000 blocks to ensure we don't miss the events
        logs = w3.eth.get_logs({
            "fromBlock": current_block - 10000,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CLAIM_TOPIC]
        })

        if not logs:
            print("No matching claim events found in this block range.")
            return

        for log in logs:
            on_chain_id = int(log['topics'][1].hex(), 16)
            
            if on_chain_id in TARGET_IDS:
                # Extract URL from hex data
                raw_data = log['data'].hex()
                if "68747470" in raw_data: # "http" in hex
                    start_index = raw_data.find("68747470")
                    img_url = bytes.fromhex(raw_data[start_index:]).decode('utf-8', 'ignore').strip('\x00')
                    
                    print(f"\n[!] Found ID {on_chain_id}")
                    print(f"[!] Image URL: {img_url}")
                    
                    # Run AI Analysis
                    result = analyze_with_gemini(img_url)
                    
                    # Parse and Print Result
                    if 'candidates' in result:
                        answer = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"[*] AI VERDICT: {answer.strip()}")
                    else:
                        print(f"[X] AI Failure: {result}")

    except Exception as e:
        print(f"[X] System Error: {e}")

if __name__ == "__main__":
    run_automated_review()
