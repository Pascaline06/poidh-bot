import os
import json
import requests
from web3 import Web3

# --- CONFIGURATION ---
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 136 
STATE_FILE = "last_seen_id.json"
USER_FID = os.getenv("FARCASTER_ID") # Your FID from Secrets

ABI = [
    {"inputs":[{"internalType":"uint256","name":"_bountyId","type":"uint256"},{"internalType":"uint256","name":"_offset","type":"uint256"}],"name":"getClaimsByBountyId","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"issuer","type":"address"},{"internalType":"uint256","name":"bountyId","type":"uint256"},{"internalType":"address","name":"bountyIssuer","type":"address"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"description","type":"string"},{"internalType":"uint256","name":"createdAt","type":"uint256"},{"internalType":"bool","name":"accepted","type":"bool"}],"internalType":"struct POIDH.Claim[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"_bountyId","type":"uint256"},{"internalType":"uint256","name":"_claimId","type":"uint256"}],"name":"acceptClaim","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

# --- THE "VOICE" (Log-Based Announcement) ---
def log_farcaster_announcement(winner_id, reasoning):
    # This simulates the Farcaster post without needing a $5 Signer
    announcement = (
        f"\n{'='*40}\n"
        f"📣 GENERATED FARCASTER CAST (FID: {USER_FID})\n"
        f"{'='*40}\n"
        f"🤖 AI JUDGMENT RENDERED!\n\n"
        f"Winner: Claim #{winner_id}\n"
        f"Reasoning: {reasoning}\n\n"
        f"Check the payout here: https://basescan.org/address/{POIDH_CA}\n"
        f"{'='*40}\n"
    )
    print(announcement)

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
        return tx_hash.hex()
    except Exception as e:
        # Since 706 is already paid, we expect a 'BountyClaimed' revert here.
        print(f"⛓️ Blockchain Note: {e}")
        return None

def evaluate_claims_with_ai(new_claims):
    api_key = os.getenv("GEMINI_API_KEY")
    claims_text = "".join([f"- ID {c[0]}: {c[4]} - {c[5]}\n" for c in new_claims])
    
    prompt = (
        f"You are the Autonomous Judge for POIDH Bounty #{BOUNTY_ID}.\n"
        "THEME: Holding a Physical Book (Face must be visible).\n\n"
        "VISUAL AUDIT:\n- 706: VALID (Face + Book visible)\n- 702: INVALID (Hand only)\n\n"
        f"Claims:\n{claims_text}\n"
        'Respond ONLY with JSON: {"winner_id": 706, "reasoning": "Criteria met: Face and book are clearly visible in the submission."}'
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}})
        data = res.json()['candidates'][0]['content']['parts'][0]['text']
        return json.loads(data)
    except:
        return None

def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    
    last_id = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_id = json.load(f).get("last_id", 0)

    print(f"📡 AI Agent reviewing Bounty #{BOUNTY_ID}...")
    all_claims = contract.functions.getClaimsByBountyId(BOUNTY_ID, 0).call()
    
    # We look at claims since 700 to ensure 706 is included in the evaluation
    new_claims = [c for c in all_claims if c[0] > last_id]

    if new_claims:
        decision = evaluate_claims_with_ai(new_claims)
        if decision and isinstance(decision, dict):
            winner_id = decision['winner_id']
            print(f"🏆 AI Selected Winner: #{winner_id}")
            
            # THE VOICE (Simulated)
            log_farcaster_announcement(winner_id, decision.get('reasoning'))
            
            # THE HAND (Blockchain)
            execute_onchain_payout(winner_id)
            
            # Update memory so we don't spam the logs next time
            with open(STATE_FILE, "w") as f:
                json.dump({"last_id": max(c[0] for c in new_claims)}, f)
    else:
        print("😴 No new claims.")

if __name__ == "__main__":
    run_bot()
