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

def execute_onchain_payout(claim_id):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    priv_key = os.getenv("BOT_PRIVATE_KEY")
    if not priv_key:
        print("⚠️ Private Key missing.")
        return
    account = w3.eth.account.from_key(priv_key)
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    try:
        txn = contract.functions.acceptClaim(BOUNTY_ID, int(claim_id)).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price,
            'chainId': 8453
        })
        signed = w3.eth.account.sign_transaction(txn, priv_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"✅ SUCCESS! https://basescan.org/tx/{tx_hash.hex()}")
    except Exception as e:
        print(f"❌ Payout Error: {e}")

def evaluate_claims_with_ai(new_claims):
    api_key = os.getenv("GEMINI_API_KEY")
    claims_text = "".join([f"- ID {c[0]}: {c[4]} - {c[5]}\n" for c in new_claims])
    
    # Updated to Gemini 3 Flash for 2026 compatibility
    model_name = "gemini-3-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = (
        f"Pick ONE winner for Bounty #{BOUNTY_ID} (Theme: Holding a Physical Book):\n{claims_text}\n"
        'Respond ONLY with JSON: {"winner_id": 123, "reasoning": "text"}'
    )

    try:
        res = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        })
        res_json = res.json()
        
        if 'error' in res_json:
            print(f"❌ AI Error: {res_json['error']['message']}")
            return None
            
        content = res_json['candidates'][0]['content']['parts'][0]['text']
        return json.loads(content)
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    last_id = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = json.load(f).get("last_id", 0)

    print(f"📡 Checking for claims newer than {last_id}...")
    all_claims = contract.functions.getClaimsByBountyId(BOUNTY_ID, 0).call()
    new_claims = [c for c in all_claims if c[0] > last_id and not c[7]]

    if new_claims:
        decision = evaluate_claims_with_ai(new_claims)
        if decision:
            print(f"🏆 Winner: #{decision['winner_id']} - {decision['reasoning']}")
            execute_onchain_payout(decision['winner_id'])
            with open(STATE_FILE, "w") as f:
                json.dump({"last_id": max(c[0] for c in new_claims)}, f)
    else:
        print("😴 No new claims.")

if __name__ == "__main__":
    run_bot()
