import os
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"

EVENT_ABI = [{
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "bountyId", "type": "uint256"},
        {"indexed": True, "name": "claimId", "type": "uint256"},
        {"indexed": False, "name": "claimer", "type": "address"},
        {"indexed": False, "name": "submission", "type": "string"}
    ],
    "name": "ClaimCreated",
    "type": "event"
}]

CONTRACT = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDR), abi=EVENT_ABI)
TARGET_BOUNTY = 136

def run_event_review():
    print(f"🤖 Searching Bounty #{TARGET_BOUNTY}...")
    
    try:
        current_block = w3.eth.block_number
        # Using a very small window of 1,000 blocks (~33 mins) to stay under RPC limits
        search_start = current_block - 1000
        
        print(f"🔎 Scanning blocks {search_start} to {current_block}...")
        
        logs = CONTRACT.events.ClaimCreated().get_logs(
            from_block=search_start,
            argument_filters={'bountyId': TARGET_BOUNTY}
        )

        if not logs:
            print(f"ℹ️ No claims found in the last 30 mins. If the claims are older, we'll need to increase the range slightly next run.")
            return

        print(f"✅ Found {len(logs)} submissions! Starting AI analysis...")
        model = genai.GenerativeModel('gemini-1.5-flash')

        for log in logs:
            claim_id = log.args.claimId
            img_url = log.args.submission
            print(f"\n--- 🔍 AI REVIEW: CLAIM #{claim_id} ---")
            
            try:
                img_resp = requests.get(img_url).content
                response = model.generate_content([
                    "Describe if a hand is holding a book, then end with VERDICT: YES or NO.",
                    {'mime_type': 'image/jpeg', 'data': img_resp}
                ])
                print(f"Analysis: {response.text}")
            except Exception as e:
                print(f"AI Error on claim {claim_id}: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_event_review()
