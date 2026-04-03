import os
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
# Ensure your GitHub Secret BASE_RPC_URL is: https://mainnet.base.org
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"

# This ABI tells the bot how to read the "Claim" receipts
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
        # We look back through the last 10,000 blocks (~5 hours of history)
        logs = CONTRACT.events.ClaimCreated().get_logs(
            fromBlock=w3.eth.block_number - 10000,
            argument_filters={'bountyId': BOUNTY_ID}
        )

        if not logs:
            print("ℹ️ No receipts found yet. The network might still be syncing.")
            return

        print(f"✅ Found {len(logs)} submissions! AI is starting review...")
        model = genai.GenerativeModel('gemini-1.5-flash')

        for log in logs:
            claim_id = log.args.claimId
            img_url = log.args.submission
            
            print(f"\n--- 🔍 AI REVIEW: CLAIM #{claim_id} ---")
            
            img_resp = requests.get(img_url).content
            response = model.generate_content([
                "Is there a human hand holding a physical book? Explain in 10 words, then end with VERDICT: YES or VERDICT: NO.",
                {'mime_type': 'image/jpeg', 'data': img_resp}
            ])
            print(f"Verdict: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_event_review()
