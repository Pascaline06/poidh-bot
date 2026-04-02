import os
import json
import requests
from web3 import Web3
import google.generativeai as genai
from eth_account import Account

# --- CONFIGURATION ---
# APIs & Social
NEYNAR_API_KEY = os.getenv('NEYNAR_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SIGNER_UUID = os.getenv('SIGNER_UUID') # For social posting

# Blockchain
RPC_URL = os.getenv('BASE_RPC_URL') # Usually Alchemy or QuickNode
PRIVATE_KEY = os.getenv('BOT_PRIVATE_KEY')
POIDH_CONTRACT_ADDRESS = "0x..." # Replace with actual POIDH contract
POIDH_ABI = json.loads('[...]') # You'll need the contract ABI here

# Initialize AI & Web3
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
w3 = Web3(Web3.HTTPProvider(RPC_URL))
bot_account = Account.from_key(PRIVATE_KEY)

def generate_bounty_idea():
    """Requirement: Create a bounty autonomously."""
    prompt = "Suggest a simple real-world task for a $5 bounty. Example: 'Take a photo of a cool tree'. Just give the task name."
    idea = ai_model.generate_content(prompt).text.strip()
    return idea

def create_poidh_bounty(title):
    """Requirement: Control own EOA and create bounty on-chain."""
    print(f"🏗️ Creating on-chain bounty: {title}")
    # This would be a contract.functions.createBounty().build_transaction() call
    # For now, we simulate the 'action' requirement
    return "TRANSACTION_HASH_HERE"

def post_to_social(message):
    """Requirement: Social Transparency & Public Reasoning."""
    url = "https://api.neynar.com/v2/farcaster/cast"
    headers = {"x-api-key": NEYNAR_API_KEY, "Content-Type": "application/json"}
    payload = {"signer_uuid": SIGNER_UUID, "text": message}
    requests.post(url, json=payload, headers=headers)

def judge_and_payout(image_url, cast_hash):
    """Requirement: Evaluate, Select, Payout, and Explain."""
    prompt = f"Does this image prove the real-world task was done? Image: {image_url}. If yes, explain why in 1 sentence starting with 'WINNER:'"
    response = ai_model.generate_content(prompt).text
    
    if "WINNER:" in response:
        print(f"💰 Match Found! Reasoning: {response}")
        
        # 1. Execute Payout On-Chain
        # tx = contract.functions.acceptClaim(...).build_transaction()
        # signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        # w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # 2. Public Explanation (Requirement 6)
        explanation = f"Bounty Paid! Reasoning: {response} Proof: {image_url}"
        post_to_social(explanation)
        return True
    return False

def main():
    print(f"🤖 Bot Online: {bot_account.address}")
    
    # 1. Autonomous Creation (If no active bounty exists)
    # logic to call create_poidh_bounty()
    
    # 2. Monitor Submissions (Neynar Search)
    # (Use your existing search logic here...)
    
    # 3. Evaluate & Payout
    # (Use the judge_and_payout logic here...)

if __name__ == "__main__":
    main()
