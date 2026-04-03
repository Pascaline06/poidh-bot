import os
import json
import requests
from web3 import Web3
import google.generativeai as genai

# --- 1. SETUP ---
POIDH_V3_ADDRESS = "0x5555fa783936c260f77385b4e153b9725fef1719"
# Update this AFTER you post your bounty link on Farcaster
TARGET_CAST_HASH = "0xf06cd879" 

W3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

with open("poidh_abi.json", "r") as f:
    CONTRACT = W3.eth.contract(address=W3.to_checksum_address(POIDH_V3_ADDRESS), abi=json.load(f))

# --- 2. THE FUNCTIONS ---

def create_bounty():
    """Bot creates the bounty on Base."""
    print("🤖 Creating Bounty on-chain...")
    tx = CONTRACT.functions.createSoloBounty(
        "B01: Physical Book Photo", 
        "Post a real photo of a physical book. AI will verify and pay."
    ).build_transaction({
        'from': os.getenv("BOT_ADDRESS"),
        'value': W3.to_wei(0.0001, 'ether'),
        'nonce': W3.eth.get_transaction_count(os.getenv("BOT_ADDRESS")),
        'gas': 300000,
        'gasPrice': W3.eth.gas_price
    })
    signed = W3.eth.account.sign_transaction(tx, os.getenv("BOT_PRIVATE_KEY"))
    tx_hash = W3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = W3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Extracting Bounty ID from the logs
    b_id = int(receipt['logs'][0]['topics'][1].hex(), 16)
    print(f"✅ SUCCESS! Bounty ID: {b_id}")
    print(f"Tx Hash: {W3.to_hex(tx_hash)}")
    return b_id

def judge_and_pay(bounty_id):
    """Bot checks Farcaster and pays the winner."""
    print(f"🤖 Monitoring Cast: {TARGET_CAST_HASH}")
    url = f"https://api.neynar.com/v2/farcaster/cast/conversation?identifier={TARGET_CAST_HASH}&type=hash"
    res = requests.get(url, headers={"x-api-key": os.getenv("NEYNAR_API_KEY")})
    replies = res.json().get('conversation', {}).get('cast', {}).get('direct_replies', [])

    for reply in replies:
        embeds = reply.get('embeds', [])
        if embeds and 'url' in embeds[0]:
            img_url = embeds[0]['url']
            model = genai.GenerativeModel('gemini-1.5-flash')
            ai_res = model.generate_content(["Is this a physical book? YES or NO:", img_url])
            
            if "YES" in ai_res.text.upper():
                winner = reply['author'].get('verifications', [None])[0]
                if winner:
                    print(f"🎯 Winner found: @{reply['author']['username']}. Paying...")
                    # In V3, you accept the first claim (index 0)
                    tx = CONTRACT.functions.acceptClaim(bounty_id, 0).build_transaction({
                        'from': os.getenv("BOT_ADDRESS"),
                        'nonce': W3.eth.get_transaction_count(os.getenv("BOT_ADDRESS")),
                        'gas': 200000,
                        'gasPrice': W3.eth.gas_price
                    })
                    signed = W3.eth.account.sign_transaction(tx, os.getenv("BOT_PRIVATE_KEY"))
                    print(f"💰 PAID! Hash: {W3.to_hex(W3.eth.send_raw_transaction(signed.rawTransaction))}")
                    return True
    return False

# --- 3. THE TOGGLE ---

if __name__ == "__main__":
    # SET TO TRUE TO CREATE. SET TO FALSE TO MONITOR/PAY.
    CREATE_MODE = True 
    
    if CREATE_MODE:
        create_bounty()
    else:
        # Replace '1' with your actual Bounty ID once created
        judge_and_pay(bounty_id=1)
