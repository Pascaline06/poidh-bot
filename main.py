import os
import json
import requests
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
W3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ABI = json.loads(os.getenv("POIDH_ABI_JSON")) # We'll pull ABI from a secret to be safe
CONTRACT = W3.eth.contract(address=W3.to_checksum_address("0x5555fa783936c260f77385b4e153b9725fef1719"), abi=ABI)

def create_the_bounty():
    """Run this to get your Bounty ID."""
    address = os.getenv("BOT_ADDRESS")
    print(f"Creating bounty for address: {address}")
    
    tx = CONTRACT.functions.createSoloBounty(
        "B01: Physical Book Photo", 
        "Post a real photo of a physical book. AI judges and pays."
    ).build_transaction({
        'from': W3.to_checksum_address(address),
        'value': W3.to_wei(0.0001, 'ether'),
        'nonce': W3.eth.get_transaction_count(address),
        'gas': 300000,
        'gasPrice': W3.eth.gas_price
    })
    
    signed = W3.eth.account.sign_transaction(tx, os.getenv("BOT_PRIVATE_KEY"))
    hash = W3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = W3.eth.wait_for_transaction_receipt(hash)
    
    # Get ID from the logs
    b_id = int(receipt['logs'][0]['topics'][1].hex(), 16)
    print(f"✅ DONE! Bounty ID is: {b_id}")
    print(f"Tx: https://basescan.org/tx/{W3.to_hex(hash)}")

if __name__ == "__main__":
    # JUST RUN THIS FOR NOW. WE WILL ADD MONITORING ONCE YOU HAVE THE ID.
    create_the_bounty()
