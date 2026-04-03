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
    print(f"🤖 Starting Full Scan for Bounty #{TARGET_BOUNTY}...")
    
    try:
        current_block = w3.eth.block_number
        # Scan the last 21,600 blocks (~12 hours) in chunks of 2000
        total_blocks_to_scan = 21600
        chunk_size = 2000
        
        found_any = False
        start_at = current_block - total_blocks_to_scan
        
        for i in range(current_block, start_at, -chunk_size):
            from_blk = max(start_at, i - chunk_size)
            to_blk = i
            
            print(f"🔎 Scanning: {from_blk} to {to_blk}...")
            
            logs = CONTRACT.events.ClaimCreated().get_logs(
                from_block=from_blk,
                to_block=to_blk,
                argument_filters={'bountyId': TARGET_BOUNTY}
            )

            if logs:
                found_any = True
                print(f"✅ SUCCESS! Found {len(logs)} submissions in this chunk.")
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
        
        if not found_any:
            print("ℹ️ Finished 12-hour scan. No claims found for this Bounty ID.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_event_review()
