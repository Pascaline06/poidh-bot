import os
from web3 import Web3

# Config
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 1122

# ABI for the 'bounties' info
ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "bounties",
        "outputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "address", "name": "issuer", "type": "address"},
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "description", "type": "string"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "uint256", "name": "claimId", "type": "uint256"},
            {"internalType": "bool", "name": "claimed", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)

    try:
        print(f"🔎 Investigating Bounty {BOUNTY_ID} on Contract {POIDH_CA}...")
        bounty = contract.functions.bounties(BOUNTY_ID).call()
        
        if bounty[1] == "0x0000000000000000000000000000000000000000":
            print("❌ This Bounty ID does not exist on this contract.")
        else:
            print(f"✅ Found it!")
            print(f"Title: {bounty[2]}")
            print(f"Issuer: {bounty[1]}")
            print(f"Is it claimed/finished?: {bounty[6]}")
            
    except Exception as e:
        print(f"❌ Error during check: {e}")

if __name__ == "__main__":
    run_bot()
