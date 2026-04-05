import os
import json
from web3 import Web3

# --- THE WINNING CONFIG ---
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 136  # Confirmed ID from our scan
STATE_FILE = "last_seen_id.json"

# V3 ABI
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
            try:
                return json.load(f).get("last_id", 0)
            except: return 0
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
        print(f"📡 Checking Bounty {BOUNTY_ID}: 'B01: Holding a Physical Book'...")
        
        # Get claims for ID 136
        claims = contract.functions.getClaimsByBountyId(BOUNTY_ID, 0).call()
        
        if not claims:
            print("📭 No claims found yet for this bounty.")
            save_last_id(0) # Create file so Git doesn't error
            return

        # Filter for only NEW claims
        new_claims = [c for c in claims if c[0] > last_seen_id]
        
        if not new_claims:
            print(f"✅ No new claims since ID {last_seen_id}.")
            return

        print(f"🔔 {len(new_claims)} NEW SUBMISSIONS FOUND!")
        
        highest_id = last_seen_id
        for c in new_claims:
            # c[0]=ID, c[1]=Issuer, c[4]=Name/Title, c[5]=Description
            print(f"\n🌟 CLAIM #{c[0]}")
            print(f"Submitted by: {c[1]}")
            print(f"Title: {c[4]}")
            print(f"Details: {c[5]}")
            
            if c[0] > highest_id:
                highest_id = c[0]

        save_last_id(highest_id)
        print(f"\n💾 Progress saved. Next check will look for IDs higher than {highest_id}.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_bot()
