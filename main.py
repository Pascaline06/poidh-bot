import os
import requests
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_IDS = [705, 706]

def analyze_with_gemini(img_url):
    # Direct API call to bypass the broken library
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {
        "contents": [{
            "parts": [
                {"text": "Is a hand holding a book? Answer YES or NO."},
                {"inline_data": {
                    "mime_type": "image/jpeg",
                    "data": requests.get(img_url).content.hex() # Sending as hex to avoid library issues
                }}
            ]
        }]
    }
    res = requests.post(url, json=payload)
    return res.json()

def run_automated_review():
    try:
        logs = w3.eth.get_logs({
            "fromBlock": w3.eth.block_number - 5000,
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
                    print(f"AI Result: {result}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_automated_review()
