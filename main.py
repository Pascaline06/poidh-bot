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
    print(f"🤖 Searching specifically for Bounty #{TARGET_BOUNTY}...")
    
    try:
        current_block = w3.eth.block_number
        # We can look back even further now because we are filtering by ID
        # Looking back 20,000 blocks (~11 hours)
        
        # This 'argument_filters' tells the node to ONLY send us Bounty 136
        logs = CONTRACT.events.ClaimCreated().get_logs(
            from_block=current_block - 20000,
            argument_filters={'bountyId': TARGET_BOUNTY}
        )

        if not logs:
            print(f"ℹ️ No claims found for Bounty #{TARGET_BOUNTY} in the last 11 hours.")
            return

        print(f"✅ Found {len(logs)} submissions! Starting AI analysis...")
        model = genai.GenerativeModel('gemini-1.5-flash')

        for log in logs:
            claim_id = log.args.claimId
            img_url = log.args.submission
            
            print(f"\n--- 🎯 MATCH FOUND: CLAIM #{claim_id} ---")
            print(f"Image Link: {img_url}")
            
            try:
                img_resp = requests.get(img_url).content
                response = model.generate_content([
                    "Describe if a hand is holding a book, then end with VERDICT: YES or NO.",
                    {'mime_type': 'image/jpeg', 'data': img_resp}
                ])
                print(f"Result: {response.text}")
            except Exception as e:
                print(f"AI Error on claim {claim_id}: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if "413" in str(e):
            print("💡 Node still overwhelmed. Try reducing the block range to 5000.")

if __name__ == "__main__":
    run_event_review()
