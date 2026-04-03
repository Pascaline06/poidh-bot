import os
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ABI_DATA = [{"inputs":[{"internalType":"uint256","name":"bountyId","type":"uint256"}],"name":"getClaims","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"claimer","type":"address"},{"internalType":"string","name":"submission","type":"string"},{"internalType":"bool","name":"accepted","type":"bool"}],"internalType":"structPOIDH.Claim[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"}]

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CONTRACT = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDR), abi=ABI_DATA)
BOUNTY_ID = 136 

def ai_review(image_url):
    try:
        img_data = requests.get(image_url).content
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Look at this image. Is a human hand clearly holding a physical book? Explain why in one sentence, then end with 'VERDICT: YES' or 'VERDICT: NO'.",
            {'mime_type': 'image/jpeg', 'data': img_data}
        ])
        return response.text
    except Exception as e:
        return f"Error reviewing image: {e}"

def run_review():
    print(f"🤖 AI Agent is reviewing claims for Bounty {BOUNTY_ID}...")
    claims = CONTRACT.functions.getClaims(BOUNTY_ID).call()
    
    for c in claims:
        claim_id, claimer, img_url, is_accepted = c
        if not is_accepted:
            print(f"\n--- 🔍 REVIEWING CLAIM #{claim_id} ---")
            analysis = ai_review(img_url)
            print(analysis)
        else:
            print(f"Claim #{claim_id} already paid.")

if __name__ == "__main__":
    run_review()
