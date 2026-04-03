import os
import json
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
# Using the correct lowercase style for the new Web3 version
w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ABI is included directly to avoid JSON secret errors
ABI_DATA = [
    {"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"description","type":"string"}],"name":"createSoloBounty","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"bountyId","type":"uint256"},{"internalType":"uint256","name":"claimId","type":"uint256"}],"name":"acceptClaim","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

CONTRACT_ADDRESS = "0x5555fa783936c260f77385b4e153b9725fef1719"
CONTRACT = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI_DATA)

def create_the_bounty():
    """Run this to get your Bounty ID."""
    bot_addr = os.getenv("BOT_ADDRESS")
    bot_key = os.getenv("BOT_PRIVATE_KEY")
    
    if not bot_addr or not bot_key:
        print("❌ Error: Secrets are still missing!")
        return

    print(f"🤖 Starting bounty creation for: {bot_addr}")
    
    # Get the latest transaction count (nonce)
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(bot_addr))
    
    tx = CONTRACT.functions.createSoloBounty(
        "B01: Physical Book Photo", 
        "Post a real photo of a physical book. AI judges and pays."
    ).build_transaction({
        'from': w3.to_checksum_address(bot_addr),
        'value': w3.to_wei(0.0001, 'ether'),
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign and Send - Fixed the raw_transaction error here
    signed = w3.eth.account.sign_transaction(tx, bot_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    print("⏳ Waiting for transaction to confirm...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Extract Bounty ID from the first log entry
    b_id = int(receipt['logs'][0]['topics'][1].hex(), 16)
    
    print(f"✅ SUCCESS! Bounty ID is: {b_id}")
    print(f"🔗 View on BaseScan: https://basescan.org/tx/{w3.to_hex(tx_hash)}")

if __name__ == "__main__":
    create_the_bounty()
