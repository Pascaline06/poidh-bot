import os
import json
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Essential ABI functions
ABI_DATA = [
    {"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"description","type":"string"}],"name":"createSoloBounty","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"bountyId","type":"uint256"},{"internalType":"uint256","name":"claimId","type":"uint256"}],"name":"acceptClaim","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

CONTRACT_ADDRESS = "0x5555fa783936c260f77385b4e153b9725fef1719"
CONTRACT = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI_DATA)

def create_the_bounty():
    bot_addr = os.getenv("BOT_ADDRESS")
    bot_key = os.getenv("BOT_PRIVATE_KEY")
    
    if not bot_addr or not bot_key:
        print("❌ Error: Secrets missing!")
        return

    my_budget_eth = 0.001 # $3.30 (Contract Minimum)
    print(f"🤖 Launching Bounty: {my_budget_eth} ETH...")
    
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(bot_addr))
    
    # Updated Task: Holding the book
    tx = CONTRACT.functions.createSoloBounty(
        "B01: Holding a Physical Book", 
        "Post a real photo of you HOLDING a physical book. AI judges and pays."
    ).build_transaction({
        'from': w3.to_checksum_address(bot_addr),
        'value': w3.to_wei(my_budget_eth, 'ether'),
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed = w3.eth.account.sign_transaction(tx, bot_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    print(f"⏳ Transaction Sent! Hash: {w3.to_hex(tx_hash)}")
    print("⏳ Waiting for Base network to confirm...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        b_id = int(receipt['logs'][0]['topics'][1].hex(), 16)
        print(f"\n🚀 BOUNTY IS LIVE!")
        print(f"✅ Bounty ID: {b_id}")
        print(f"🔗 Link: https://poidh.xyz/bounty/{b_id}")
    else:
        print(f"❌ Transaction Failed. Check your balance or BaseScan.")

if __name__ == "__main__":
    create_the_bounty()
