import os, requests, json
from web3 import Web3
import google.generativeai as genai

# --- CONFIGURATION ---
POIDH_CONTRACT_ADDRESS = "0x5555fa783936c260f77385b4e153b9725fef1719" # Confirm on POIDH docs
W3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

with open('poidh_abi.json') as f:
    CONTRACT = W3.eth.contract(address=W3.to_checksum_address(POIDH_CONTRACT_ADDRESS), abi=json.load(f))

def get_farcaster_submissions(cast_hash): "https://farcaster.xyz/pascaline/0xf06cd879"
    url = f"https://api.neynar.com/v2/farcaster/cast/conversation?identifier={cast_hash}&type=hash"
    res = requests.get(url, headers={"x-api-key": os.getenv("NEYNAR_API_KEY")})
    return res.json().get('conversation', {}).get('cast', {}).get('direct_replies', [])

def judge_with_gemini(image_url):
    model = genai.GenerativeModel('gemini-1.5-flash')
    # This prompt enforces the "Real World" requirement
    prompt = "Look at this image. Is it a photo of a human completing a physical task? Answer 'YES' or 'NO' followed by your reasoning."
    response = model.generate_content([prompt, image_url])
    return response.text

def payout_on_poidh(bounty_id, winner_address):
    """Calls the actual POIDH contract to pay the winner"""
    nonce = W3.eth.get_transaction_count(os.getenv("BOT_ADDRESS"))
    tx = CONTRACT.functions.payout(bounty_id, winner_address).build_transaction({
        'from': os.getenv("BOT_ADDRESS"),
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': W3.eth.gas_price
    })
    signed = W3.eth.account.sign_transaction(tx, os.getenv("BOT_PRIVATE_KEY"))
    return W3.eth.send_raw_transaction(signed.rawTransaction)

# --- RUN LOGIC ---
BOUNTY_ID = 123 # Replace with your actual POIDH Bounty ID
CAST_HASH = "0x..." # Your Farcaster Post Hash

for sub in get_farcaster_submissions(CAST_HASH):
    img = sub.get('embeds', [{}])[0].get('url')
    if img:
        reasoning = judge_with_gemini(img)
        if "YES" in reasoning.upper():
            print(f"Decision: {reasoning}")
            tx = payout_on_poidh(BOUNTY_ID, sub['author']['verifications'][0])
            print(f"Bounty Paid! TX: {tx.hex()}")
