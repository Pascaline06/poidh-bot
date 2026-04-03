import os
from web3 import Web3

# --- CONFIG ---
w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))

# The contract address on Base
CONTRACT_ADDRESS = "0x5555fa783936c260f77385b4e153b9725fef1719"

ABI_DATA = [
    {"inputs":[{"internalType":"uint256","name":"bountyId","type":"uint256"}],"name":"getClaims","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"claimer","type":"address"},{"internalType":"string","name":"submission","type":"string"},{"internalType":"bool","name":"accepted","type":"bool"}],"internalType":"structPOIDH.Claim[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"}
]

CONTRACT = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI_DATA)
BOUNTY_ID = 136 # Your successful bounty

def check_the_claim():
    print(f"🔍 Fetching claims for Bounty #{BOUNTY_ID}...")
    claims = CONTRACT.functions.getClaims(BOUNTY_ID).call()
    
    if not claims:
        print("Empty? Maybe the transaction is still syncing. Try again in a minute.")
        return

    for c in claims:
        print(f"\n--- New Claim Found! ---")
        print(f"ID: {c[0]}")
        print(f"User: {c[1]}")
        print(f"Photo Link: {c[2]}")
        print(f"Status: {'Paid' if c[3] else 'Pending'}")

if __name__ == "__main__":
    check_the_claim()
