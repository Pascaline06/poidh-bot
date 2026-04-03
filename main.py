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
BOUNTY_ID = 136

def run_event_review():
    print(f"🤖 Searching for Bounty #{BOUNTY_ID} receipts...")
    
    try:
        current_block = w3.eth.block_number
        # We increase this to 100,000 blocks (~2 days of history)
        search_start = current_block - 100000 
        
        print(f"🔎 Scanning from block {search_start} to {current_block}...")
        
        logs = CONTRACT.events.ClaimCreated().get_logs(
            from_block=search_start
        )

        bounty_logs = [log for log in logs if log.args.bountyId == BOUNTY_ID]

        if not bounty_logs:
            print("ℹ️ Still no receipts found. Increasing search range might be needed.")
            return

        print(f"✅ Success! Found {len(bounty_logs)} submissions! AI is starting review...")
        model = genai.GenerativeModel('gemini-1.5-flash')

        for log in bounty_logs:
            claim_id = log.args.claimId
            img_url = log.args.submission
            
            print(f"\n--- 🔍 AI REVIEW: CLAIM #{claim_id} ---")
            
            try:
                img_resp = requests.get(img_url).content
                response = model.generate_content([
                    "Is there a human hand holding a physical book? Explain in 10 words, then end with VERDICT: YES or VERDICT: NO.",
                    {'mime_type': 'image/jpeg', 'data': img_resp}
                ])
                print(f"Verdict: {response.text}")
            except Exception as e:
                print(f"Error analyzing image for claim {claim_id}: {e}")

    except Exception as e:
        print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    run_event_review()
