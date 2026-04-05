import os
import json
from web3 import Web3

# Config
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 1122
STATE_FILE = "last_seen_id.json"

# The corrected V3 ABI
ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "_bountyId", "type": "uint256"},
            {"internalType": "uint256", "name": "_offset", "type": "uint256"}
        ],
        "name": "getClaimsByBountyId",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "address", "name": "issuer", "type": "address"},
                    {"internalType": "uint256", "name": "bountyId", "type": "uint256"},
                    {"internalType": "address", "name": "bountyIssuer", "type": "address"},
                    {"internalType": "string", "name": "name", "type": "string"},
                    {"internalType": "string", "name": "description", "type": "string"},
                    {"internalType": "uint256", "name": "createdAt", "type": "uint256"},
                    {"internalType": "bool", "name": "accepted", "type": "bool"}
                ],
                "internalType": "struct POIDH.Claim[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def load_last_id():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("last_id", 0)
    return 0

def save_last_id(last_id):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_id": last_id}, f)

def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Connection failed")
        return

    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    last_seen_id = load_last_id()

    try:
        print(f"📡 Checking Bounty {BOUNTY_ID} (Last seen Claim ID: {last_seen_id})...")
        
        # We pass BOUNTY_ID and 0 (offset) to get the first 10 claims
        claims = contract.functions.getClaimsByBountyId(BOUNTY_ID, 0).call()
        
        if not claims:
            print("📭 No claims found.")
            return

        new_claims = [c for c in claims if c[0] > last_seen_id]
        
        if not new_claims:
            print("✅ No new claims since last check.")
            return

        print(f"🔔 FOUND {len(new_claims)} NEW CLAIMS!")
        
        highest_id = last_seen_id
        for c in new_claims:
            cid, issuer, b_id, b_iss, name, desc, time, accepted = c
            print(f"\n--- NEW CLAIM #{cid} ---")
            print(f"From: {issuer}")
            print(f"Title: {name}")
            print(f"Description: {desc}")
            
            if cid > highest_id:
                highest_id = cid

        # Update the state so we don't notify for these again
        save_last_id(highest_id)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_bot()
