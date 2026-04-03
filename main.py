import os
import json
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
W3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# I've put the ABI here directly so you don't need a secret for it anymore
ABI_DATA = [{"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"description","type":"string"}],"name":"createSoloBounty","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"bountyId","type":"uint256"},{"internalType":"uint256","name":"claimId","type":"uint256"}],"name":"acceptClaim","outputs":[],"stateMutability":"nonpayable","type":"function"}]

CONTRACT_ADDRESS = "0x5555fa783936c260f77385b4e153b9725fef1719"
CONTRACT = W3.eth.contract(address=W3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI_DATA)

def create_the_bounty():
    """Run this to get your Bounty ID."""
    # We pull these from your GitHub Secrets
    bot_addr = os.getenv("BOT_ADDRESS")
    bot_key = os.getenv("BOT_PRIVATE_KEY")
    
    if not bot_addr or not bot_key:
        print("❌ Error: BOT_ADDRESS or BOT_PRIVATE_KEY is missing from GitHub Secrets!")
        return

    print(f"🤖 Starting bounty creation for: {bot_addr}")
    
    tx = CONTRACT.functions.createSoloBounty(
        "B01: Physical Book Photo", 
        "Post a real photo of a physical book. AI judges and pays."
    ).build_transaction({
        'from': W3.to_checksum_address(bot_addr),
        'value': W3.to_wei(0.0001, 'ether'),
        'nonce': W3.eth.get_transaction_count(bot_addr),
        'gas': 300000,
        'gasPrice': W3.eth.gas_price
    })
    
    signed = W3.eth.account.sign_transaction(tx, bot_key)
    tx_hash = W3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = W3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Get ID from the transaction logs
    b_id = int(receipt['logs'][0]['topics'][1].hex(), 16)
    print(f"✅ SUCCESS! Bounty ID is: {b_id}")
    print(f"Tx: https://basescan.org/tx/{W3.to_hex(tx_hash)}")

if __name__ == "__main__":
    create_the_bounty()
