import os
import json
from web3 import Web3
import google.generativeai as genai

# --- CONFIG ---
w3 = Web3(Web3.HTTPProvider(os.getenv("BASE_RPC_URL")))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ABI_DATA = [
    {"inputs":[],"name":"MIN_BOUNTY_AMOUNT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
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

    # --- BUDGET CHECK ---
    # This checks the contract's rules so we don't waste money
    min_amt_wei = CONTRACT.functions.MIN_BOUNTY_AMOUNT().call()
    min_amt_eth = w3.from_wei(min_amt_wei, 'ether')
    print(f"📊 Contract Minimum Requirement: {min_amt_eth} ETH")

    my_budget_eth = 0.0003 # This is approx $1.00
    
    if my_budget_eth < min_amt_eth:
        print(f"⚠️ Warning: Your $1 ({my_budget_eth} ETH) is lower than the contract minimum ({min_amt_eth} ETH).")
        print("The transaction will likely fail. You may need to use the minimum amount shown above.")
        return

    print(f"🤖 Creating bounty with budget: {my_budget_eth} ETH")
    
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(bot_addr))
    
    tx = CONTRACT.functions.createSoloBounty(
        "B01: Physical Book Photo", 
        "Post a real photo of a physical book. AI judges and pays."
    ).build_transaction({
        'from': w3.to_checksum_address(bot_addr),
        'value': w3.to_wei(my_budget_eth, 'ether'),
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed = w3.eth.account.sign_transaction(tx, bot_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    print(f"⏳ Tx Sent: {w3.to_hex(tx_hash)}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1 and len(receipt['logs']) > 0:
        b_id = int(receipt['logs'][0]['topics'][1].hex(), 16)
        print(f"✅ SUCCESS! Bounty ID: {b_id}")
        print(f"🔗 Link: https://poidh.xyz/bounty/{b_id}")
    else:
        print(f"❌ REVERTED. View: https://basescan.org/tx/{w3.to_hex(tx_hash)}")

if __name__ == "__main__":
    create_the_bounty()
