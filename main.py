import os
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Simplified ABI focused on the actual structure of the POIDH contract
ABI_DATA = [
    {
        "inputs": [{"internalType": "uint256", "name": "bountyId", "type": "uint256"}],
        "name": "getClaims",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "address", "name": "claimer", "type": "address"},
                    {"internalType": "string", "name": "submission", "type": "string"},
                    {"internalType": "bool", "name": "accepted", "type": "bool"}
                ],
                "internalType": "struct POIDH.Claim[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CONTRACT = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDR), abi=ABI_DATA)
BOUNTY_ID = 136 

def run_review():
    print(f"🤖 Agent Starting... Bounty #{BOUNTY_ID}")
    
    try:
        # We wrap the call in a more robust fetch
        claims = CONTRACT.functions.getClaims(BOUNTY_ID).call()
        
        if not claims:
            print("ℹ️ Contract returned 0 claims. If you see them on the site, the RPC is lagging.")
            return

        print(f"✅ Success! Found {len(claims)} claims.")
        model = genai.GenerativeModel('gemini-1.5-flash')

        for c in claims:
            # Struct mapping: id=0, claimer=1, url=2, accepted=3
            if not c[3]:
                print(f"\n--- 🔍 AI REVIEW: CLAIM #{c[0]} ---")
                img_url = c[2]
                print(f"Downloading: {img_url}")
                
                img_resp = requests.get(img_url).content
                response = model.generate_content([
                    "Does this image show a human hand holding a physical book? Explain in 10 words, then end with VERDICT: YES or VERDICT: NO.",
                    {'mime_type': 'image/jpeg', 'data': img_resp}
                ])
                print(f"Analysis: {response.text}")
            else:
                print(f"Claim #{c[0]} is already settled.")
                
    except Exception as e:
        print(f"❌ FETCH ERROR: {e}")
        print("💡 TIP: If you see 'execution reverted', try one more time in 2 minutes. Blockchain nodes sometimes 'blink'.")

if __name__ == "__main__":
    run_review()
