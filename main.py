import os
import json
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIGURATION ---
POIDH_V2_ADDRESS = "0x5555fa783936c260f77385b4e153b9725fef1719"
# You will update this after you manually post the bounty link
TARGET_CAST_HASH = "0xf06cd879" 

W3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

with open("poidh_abi.json", "r") as f:
    CONTRACT = W3.eth.contract(address=W3.to_checksum_address(POIDH_V2_ADDRESS), abi=json.load(f))

# --- PHASE 1: AUTONOMOUS CREATION ---
def create_bounty_on_chain():
    """Requirement: 'Create a real-world-action bounty on poidh'"""
    print("🤖 Step 1: Creating Bounty on Base...")
    
    # We use 'createSoloBounty' (Title, Description, Amount)
    # Adjust parameters based on the specific POIDH V2 ABI you have
    tx = CONTRACT.functions.createSoloBounty(
        "Photo of a Physical Book", 
        "Reply with a real photo of a printed book to win 0.0001 ETH.",
        "0x0000000000000000000000000000000000000000" # Open to anyone
    ).build_transaction({
        'from': os.getenv("BOT_ADDRESS"),
        'value': W3.to_wei(0.0001, 'ether'),
        'nonce': W3.eth.get_transaction_count(os.getenv("BOT_ADDRESS")),
        'gas': 300000,
        'gasPrice': W3.eth.gas_price
    })
    
    signed_tx = W3.eth.account.sign_transaction(tx, os.getenv("BOT_PRIVATE_KEY"))
    tx_hash = W3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"✅ Bounty Created! Tx: {W3.to_hex(tx_hash)}")
    return W3.to_hex(tx_hash)

# --- PHASE 2: MONITOR & JUDGE ---
def judge_and_pay():
    print(f"🤖 Step 2: Monitoring Farcaster Cast {TARGET_CAST_HASH}...")
    
    url = f"https://api.neynar.com/v2/farcaster/cast/conversation?identifier={TARGET_CAST_HASH}&type=hash"
    res = requests.get(url, headers={"x-api-key": os.getenv("NEYNAR_API_KEY")})
    replies = res.json().get('conversation', {}).get('cast', {}).get('direct_replies', [])

    for reply in replies:
        embeds = reply.get('embeds', [])
        if embeds and 'url' in embeds[0]:
            img_url = embeds[0]['url']
            print(f"Checking submission from @{reply['author']['username']}...")

            # AI Evaluation
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Is this a real photo of a physical book? Answer ONLY 'YES' or 'NO'."
            ai_res = model.generate_content(["Analyze this image:", img_url, prompt])
            
            if "YES" in ai_res.text.upper():
                winner_wallet = reply['author'].get('verifications', [None])[0]
                if winner_wallet:
                    print(f"🎯 MATCH! AI Reason: {ai_res.text}")
                    execute_payout(winner_wallet)
                    return True # Stop after first winner
    return False

def execute_payout(address):
    """Requirement: 'Execute the payout on-chain'"""
    # Note: You'll need the Bounty ID from your Create transaction
    # For the demo, ensure you know your ID (usually found in event logs)
    BOUNTY_ID = 1 
    
    tx = CONTRACT.functions.acceptClaim(BOUNTY_ID, 0).build_transaction({
        'from': os.getenv("BOT_ADDRESS"),
        'nonce': W3.eth.get_transaction_count(os.getenv("BOT_ADDRESS")),
        'gas': 200000,
        'gasPrice': W3.eth.gas_price
    })
    signed = W3.eth.account.sign_transaction(tx, os.getenv("BOT_PRIVATE_KEY"))
    print(f"💰 Payout Sent! Hash: {W3.to_hex(W3.eth.send_raw_transaction(signed.rawTransaction))}")

if __name__ == "__main__":
    # If you haven't created the bounty yet, run this once:
    # create_bounty_on_chain()
    
    # Once you've posted the link to Farcaster, run this:
    judge_and_pay()
