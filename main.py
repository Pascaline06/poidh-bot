import os
from web3 import Web3

# Config
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"

# The two different "buildings" (Contracts)
V2_ADDRESS = "0xb509E5Ea381C43e9A9E96E6999a0E8218151f8B4"
V3_ADDRESS = "0x5555Fa783936C260f77385b4E153B9725feF1719"

# Simple ABI for checking bounty info
ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "bounties",
        "outputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "address", "name": "issuer", "type": "address"},
            {"internalType": "string", "name": "name", "type": "string"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def check_bounty(w3, contract_addr, bounty_id, version_label):
    try:
        contract = w3.eth.contract(address=w3.to_checksum_address(contract_addr), abi=ABI)
        bounty = contract.functions.bounties(bounty_id).call()
        if bounty[1] != "0x0000000000000000000000000000000000000000":
            print(f"✅ FOUND on {version_label}! ID: {bounty_id} | Name: {bounty[2]}")
            return True
    except:
        print(f"❌ Not found on {version_label} with ID {bounty_id}")
    return False

def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    print("📡 Scanning Base Chain for your bounty...")
    
    # Check 136 on V2
    check_bounty(w3, V2_ADDRESS, 136, "V2 Contract")
    
    # Check 1122 on V3
    check_bounty(w3, V3_ADDRESS, 1122, "V3 Contract")
    
    # Check 136 on V3 (just in case)
    check_bounty(w3, V3_ADDRESS, 136, "V3 Contract")

if __name__ == "__main__":
    run_bot()
