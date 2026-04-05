import os
import json
from web3 import Web3

# Config
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 1122

# Minimal ABI to tell Python how to talk to the "getClaimsByBountyId" function
ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "_bountyId", "type": "uint256"}],
        "name": "getClaimsByBountyId",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "address", "name": "issuer", "type": "address"},
                    {"internalType": "string", "name": "uri", "type": "string"}
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

def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Connection failed")
        return

    # Connect to the contract
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)

    try:
        print(f"📡 Requesting all claims for Bounty {BOUNTY_ID}...")
        # This is the "Magic" call that ignores block limits
        claims = contract.functions.getClaimsByBountyId(BOUNTY_ID).call()
        
        if not claims:
            print("📭 No claims found yet for this bounty.")
            return

        print(f"✨ Found {len(claims)} total claims!")
        
        for c in claims:
            # c[0] is ID, c[1] is address, c[2] is the IPFS/Link
            print(f"--- Claim #{c[0]} ---")
            print(f"Issuer: {c[1]}")
            print(f"Content: {c[2]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_bot()
