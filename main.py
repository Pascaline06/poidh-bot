import os
import requests
import base64
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_IDS = [705, 706]

def analyze_with_gemini(img_url):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # Download the image and convert to Base64 string
    img_response = requests.get(img_url)
    img_b64 = base64.b64encode(img_response.content).decode('utf-8')
    
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
    res = requests.post(url, json=payload)
    return res.json()

def run_automated_review():
    try:
        current_block = w3.eth.block_number
        logs = w3.eth.get_logs({
            "fromBlock": current_block - 5000,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CLAIM_TOPIC]
        })

        for log in logs:
            on_chain_id = int(log['topics'][1].hex(), 16)
            if on_chain_id in TARGET_IDS:
                raw_data = log['data'].hex()
                if "68747470" in raw_data:
                    img_url = bytes.fromhex(raw_data[raw_data.find("68747470"):]).decode('utf-8', 'ignore').strip('\x00')
                    print(f"Reviewing ID {on_chain_id}: {img_url}")
                    result = analyze_with_gemini(img_url)
                    
                    # Clean output to see the AI's answer clearly
                    try:
                        answer = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"AI VERDICT: {answer.strip()}")
                    except:
                        print(f"AI Error: {result}")

    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    run_automated_review()
