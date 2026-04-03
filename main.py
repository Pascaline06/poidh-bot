import os
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_IDS = [705, 706] 

def run_automated_review():
    try:
        current_block = w3.eth.block_number
        logs = w3.eth.get_logs({
            "fromBlock": current_block - 5000, 
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CLAIM_TOPIC]
        })

        if not logs:
            print("No claims found.")
            return

        # This will now work because we updated the requirements.txt
        model = genai.GenerativeModel('gemini-1.5-flash')

        for log in logs:
            on_chain_id = int(log['topics'][1].hex(), 16)
            if on_chain_id in TARGET_IDS:
                raw_data = log['data'].hex()
                if "68747470" in raw_data: 
                    img_url = bytes.fromhex(raw_data[raw_data.find("68747470"):]).decode('utf-8', 'ignore').strip('\x00')
                    print(f"Reviewing: {img_url}")
                    img_data = requests.get(img_url).content
                    response = model.generate_content([
                        "Is a hand holding a book? VERDICT: YES or NO.",
                        {'mime_type': 'image/jpeg', 'data': img_data}
                    ])
                    print(f"ID {on_chain_id} Result: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_automated_review()
