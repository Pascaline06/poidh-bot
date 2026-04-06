import os
import json
import requests
from web3 import Web3

# --- CONFIGURATION ---
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 136 
STATE_FILE = "last_seen_id.json"

ABI = [
    {"inputs":[{"internalType":"uint256","name":"_bountyId","type":"uint256"},{"internalType":"uint256","name":"_offset","type":"uint256"}],"name":"getClaimsByBountyId","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"issuer","type":"address"},{"internalType":"uint256","name":"bountyId","type":"uint256"},{"internalType":"address","name":"bountyIssuer","type":"address"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"description","type":"string"},{"internalType":"uint256","name":"createdAt","type":"uint256"},{"internalType":"bool","name":"accepted","type":"bool"}],"internalType":"struct POIDH.Claim[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"_bountyId","type":"uint256"},{"internalType":"uint256","name":"_claimId","type":"uint256"}],"name":"acceptClaim","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

def evaluate_claims_with_vision(new_claims):
    api_key = os.getenv("GEMINI_API_KEY")
    
    # We build a prompt that includes the IMAGE URL for every claim
    # POIDH stores the image URL in the 'description' or 'name' field usually
    # For this demo, we assume the AI can access the URL from the metadata
    
    parts = [{"text": "You are the Autonomous Judge. Look at the images for these bounty claims. "
                     "The goal is 'Holding a Physical Book'. A human face MUST be visible. "
                     "Reject any entry that only shows hands or just the book."}]

    for c in new_claims:
        # We append the text and the metadata for the AI to analyze
        parts.append({"text": f"Claim ID {c[0]}: {c[5]} (Description: {c[5]})"})
        # Note: In a production bot, we would fetch the actual image URL from the POIDH API 
        # and add it here so Gemini can 'see' it.

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        res = requests.post(url, json=payload)
        return json.loads(res.json()['candidates'][0]['content']['parts'][0]['text'])
    except:
        return None

def execute_onchain_payout(claim_id):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    priv_key = os.getenv("BOT_PRIVATE_KEY")
    account = w3.eth.account.from_key(priv_key)
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    try:
        txn = contract.functions.acceptClaim(BOUNTY_ID, int(claim_id)).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 300000, 
            'gasPrice': w3.eth.gas_price,
            'chainId': 8453
        })
        signed = w3.eth.account.sign_transaction(txn, priv_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ Success: {tx_hash.hex()}")
    except Exception as e:
        print(f"❌ Reverted: {e}")

def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    
    last_id = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = json.load(f).get("last_id", 0)

    all_claims = contract.functions.getClaimsByBountyId(BOUNTY_ID, 0).call()
    new_claims = [c for c in all_claims if c[0] > last_id and not c[7]]

    if new_claims:
        # THE AI DECIDES FREELY
        decision = evaluate_claims_with_vision(new_claims)
        if decision:
            print(f"🏆 AI Selected #{decision['winner_id']} based on its own analysis.")
            execute_onchain_payout(decision['winner_id'])
            with open(STATE_FILE, "w") as f:
                json.dump({"last_id": max(c[0] for c in new_claims)}, f)
    else:
        print("😴 No new claims.")

if __name__ == "__main__":
    run_bot()
