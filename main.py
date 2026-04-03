import os
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
# Double check this in your Secrets! It should be exactly: https://mainnet.base.org
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the exact POIDH ABI for the getClaims function
ABI_DATA = [{"inputs":[{"internalType":"uint256","name":"bountyId","type":"uint256"}],"name":"getClaims","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"claimer","type":"address"},{"internalType":"string","name":"submission","type":"string"},{"internalType":"bool","name":"accepted","type":"bool"}],"internalType":"structPOIDH.Claim[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"}]

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CONTRACT = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDR), abi=ABI_DATA)
BOUNTY_ID = 136 

def run_review():
    print(f"🔗 Connected to RPC: {RPC_URL}")
    print(f"🤖 Fetching Bounty #{BOUNTY_ID} on Base...")
    
    try:
        # We add 'latest' block identifier to ensure we get the most recent data
        claims = CONTRACT.functions.getClaims(BOUNTY_ID).call(block_identifier='latest')
        
        if not claims:
            print("ℹ️ The contract returned an empty list. No claims found yet.")
            return

        print(f"✅ Found {len(claims)} claims! Starting AI review...")
        
        model = genai.GenerativeModel('gemini-1.5-flash')

        for c in claims:
            claim_id, claimer, img_url, is_accepted = c
            if not is_accepted:
                print(f"\n--- 🔍 REVIEWING CLAIM #{claim_id} ---")
                img_resp = requests.get(img_url).content
                response = model.generate_content([
                    "Is a human hand clearly holding a physical book? Explain briefly, then 'VERDICT: YES' or 'VERDICT: NO'.",
                    {'mime_type': 'image/jpeg', 'data': img_resp}
                ])
                print(f"Image: {img_url}")
                print(f"Result: {response.text}")
            else:
                print(f"Claim #{claim_id} already paid.")
                
    except Exception as e:
        print(f"❌ BLOCKCHAIN ERROR: {e}")
        print("Note: If it says 'execution reverted', try running again in 5 minutes.")

if __name__ == "__main__":
    run_review()
