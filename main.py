import os
import json
import requests
from web3 import Web3
import google.generativeai as genai

# 1. SETTINGS & CONNECTIONS
# This is the V2 address you found, properly formatted
POIDH_CONTRACT_ADDRESS = "0x5555fa783936c260f77385b4e153b9725fef1719"
TARGET_CAST_HASH = "0xf06cd879"

# Load environment variables from GitHub Secrets
W3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load the ABI file (make sure poidh_abi.json is in your repo!)
with open("poidh_abi.json", "r") as f:
    abi = json.load(f)
    # This fix ensures Web3.py doesn't complain about address formatting
    CONTRACT = W3.eth.contract(
        address=W3.to_checksum_address(POIDH_CONTRACT_ADDRESS), 
        abi=abi
    )

def check_farcaster_replies(cast_hash):
    """Checks for image replies to your specific post."""
    url = f"https://api.neynar.com/v2/farcaster/cast/conversation?identifier={cast_hash}&type=hash"
    headers = {"x-api-key": os.getenv("NEYNAR_API_KEY")}
    response = requests.get(url, headers=headers)
    return response.json().get('conversation', {}).get('cast', {}).get('direct_replies', [])

def judge_photo(image_url):
    """Uses Gemini Vision to verify if the photo is a real-world action."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "Analyze this image. Is it a real-world photo of a physical task? Answer 'YES' or 'NO' and give a short reason."
    response = model.generate_content([prompt, image_url])
    return response.text

def execute_poidh_payout(winner_address):
    """Sends the payout via the POIDH contract on Base."""
    # Note: Bounty ID 1 is a placeholder. Update this to your real Bounty ID if needed.
    bounty_id = 1 
    
    nonce = W3.eth.get_transaction_count(os.getenv("BOT_ADDRESS"))
    tx = CONTRACT.functions.payout(bounty_id, W3.to_checksum_address(winner_address)).build_transaction({
        'from': os.getenv("BOT_ADDRESS"),
        'nonce': nonce,
        'gas': 150000,
        'gasPrice': W3.eth.gas_price
    })
    
    signed_tx = W3.eth.account.sign_transaction(tx, os.getenv("BOT_PRIVATE_KEY"))
    tx_hash = W3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

def run_bot():
    print(f"Checking for replies on cast: {TARGET_CAST_HASH}...")
    replies = check_farcaster_replies(TARGET_CAST_HASH)
    
    for reply in replies:
        # Look for images in the reply
        embeds = reply.get('embeds', [])
        if embeds and 'url' in embeds[0]:
            image_url = embeds[0]['url']
            print(f"Found image: {image_url}. Judging...")
            
            judgment = judge_photo(image_url)
            print(f"AI Judgment: {judgment}")
            
            if "YES" in judgment.upper():
                # Get the winner's wallet address from Farcaster
                verifications = reply['author'].get('verifications', [])
                if verifications:
                    winner_wallet = verifications[0]
                    print(f"Winner found! Paying {winner_wallet}...")
                    tx = execute_poidh_payout(winner_wallet)
                    print(f"Transaction Success: {tx}")
                else:
                    print("Winner found, but they have no verified wallet on Farcaster.")

if __name__ == "__main__":
    run_bot()
