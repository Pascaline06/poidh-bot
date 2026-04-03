import os
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
# This is the exact signature we found in Run #68
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_BOUNTY = 136

def run_final_review():
    print(f"🤖 Monitoring Bounty #{TARGET_BOUNTY} via Verified Topic...")
    
    try:
        current_block = w3.eth.block_number
        # Search the last 10,000 blocks (~5.5 hours)
        logs = w3.eth.get_logs({
            "fromBlock": current_block - 10000,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR),
            "topics": [CLAIM_TOPIC]
        })

        found_claims = []
        for log in logs:
            # Topic[1] is the Bounty ID in hex. Convert to int to check if it's #136
            bounty_id = int(log['topics'][1].hex(), 16)
            if bounty_id == TARGET_BOUNTY:
                # The image URL is in the 'data' field, we need to decode it
                data = log['data'].hex()
                # Image URLs in these logs start after the offset and length headers
                # This finds the hex for 'http' and decodes to the end
                if "68747470" in data: # hex for 'http'
                    img_url = bytes.fromhex(data[data.find("68747470"):]).decode('utf-8', 'ignore').strip('\x00')
                    found_claims.append(img_url)

        if not found_claims:
            print(f"ℹ️ No new claims found for #{TARGET_BOUNTY} in the last 10k blocks.")
            return

        print(f"✅ SUCCESS! Found {len(found_claims)} submissions. AI is analyzing...")
        model = genai.GenerativeModel('gemini-1.5-flash')

        for i, url in enumerate(found_claims):
            print(f"\n--- 🔍 AI REVIEW: SUBMISSION {i+1} ---")
            print(f"Link: {url}")
            
            img_resp = requests.get(url).content
            response = model.generate_content([
                "Describe if a hand is holding a book, then end with VERDICT: YES or NO.",
                {'mime_type': 'image/jpeg', 'data': img_resp}
            ])
            print(f"Analysis: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_final_review()
