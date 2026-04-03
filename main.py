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
    print(f"🤖 Searching Bounty #{TARGET_BOUNTY} in DEEP historical window...")
    
    try:
        current_block = w3.eth.block_number
        
        # Shifting further back:
        # search_end = 4 hours ago (7,200 blocks)
        # search_start = 8 hours ago (14,400 blocks)
        search_end = current_block - 7200
        search_start = current_block - 14400
        
        print(f"🔎 Scanning blocks {search_start} to {search_end}...")
        
        logs = CONTRACT.events.ClaimCreated().get_logs(
            from_block=search_start,
            to_block=search_end,
            argument_filters={'bountyId': TARGET_BOUNTY}
        )

        if not logs:
            print(f"ℹ️ Still no claims found. They might be even older or under a different Bounty ID.")
            return

        print(f"✅ FOUND {len(logs)} SUBMISSIONS! Analyzing now...")
        model = genai.GenerativeModel('gemini-1.5-flash')

        for log in logs:
            claim_id = log.args.claimId
            img_url = log.args.submission
            print(f"\n--- 🔍 AI REVIEW: CLAIM #{claim_id} ---")
            
            img_resp = requests.get(img_url).content
            response = model.generate_content([
                "Describe if a hand is holding a book, then end with VERDICT: YES or NO.",
                {'mime_type': 'image/jpeg', 'data': img_resp}
            ])
            print(f"Analysis: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_event_review()
