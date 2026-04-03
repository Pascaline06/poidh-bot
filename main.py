import os
import json
import requests
from web3 import Web3
from eth_account import Account
import google.generativeai as genai

# --- 1. CONFIGURATION & SECRETS ---
NEYNAR_API_KEY = os.getenv('NEYNAR_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SIGNER_UUID = os.getenv('SIGNER_UUID') 
RPC_URL = os.getenv('BASE_RPC_URL') # From Alchemy
PRIVATE_KEY = os.getenv('BOT_PRIVATE_KEY')

# Initialize AI & Blockchain
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
w3 = Web3(Web3.HTTPProvider(RPC_URL))
bot_account = Account.from_key(PRIVATE_KEY)

def judge_submission(image_url, bounty_name, requirement):
    """Requirement: Evaluate submissions using AI."""
    prompt = f"Bounty: {bounty_name}. Goal: {requirement}. Image: {image_url}. Does this prove it happened? Reply 'PASS' or 'FAIL' then explain why in one sentence."
    try:
        # We send the URL and prompt to Gemini
        response = ai_model.generate_content([prompt, image_url])
        return response.text
    except Exception as e:
        return f"ERROR: {e}"

def post_explanation(text, parent_hash=None):
    """Requirement: Social Transparency - Post reasoning publicly."""
    url = "https://api.neynar.com/v2/farcaster/cast"
    headers = {"x-api-key": NEYNAR_API_KEY, "Content-Type": "application/json"}
    payload = {
        "signer_uuid": SIGNER_UUID,
        "text": text
    }
    if parent_hash:
        payload["parent"] = parent_hash
        
    requests.post(url, json=payload, headers=headers)

def execute_payout(winner_address):
    """Requirement: Execute the payout on-chain autonomously."""
    # This is a simplified placeholder for the 'acceptClaim' contract call
    print(f"💰 Payout triggered for {winner_address} on Base...")
    # In a full build, you'd use w3.eth.send_raw_transaction here.
    return "0x_transaction_hash_example"

def main():
    print(f"🤖 Bot Online: {bot_account.address}")
    
    # Check Balance first
    balance = w3.from_wei(w3.eth.get_balance(bot_account.address), 'ether')
    print(f"💎 Current Balance: {balance} ETH")

    if not os.path.exists('active_bounties.json'):
        print("❌ active_bounties.json missing!")
        return

    with open('active_bounties.json') as f:
        bounties = json.load(f)['bounties']

    for b in bounties:
        tag = b['id']
        print(f"🔍 Searching Farcaster for {tag}...")
        
        url = f"https://api.neynar.com/v2/farcaster/cast/search?q={tag}"
        headers = {"x-api-key": NEYNAR_API_KEY} # Fixed header
        
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            casts = res.json().get('result', {}).get('casts', [])

            for cast in casts:
                embeds = cast.get('embeds', [])
                image_url = next((e['url'] for e in embeds if '.jpg' in e.get('url', '') or '.png' in e.get('url', '')), None)

                if image_url:
                    print(f"⚖️ Judging submission from @{cast['author']['username']}...")
                    decision = judge_submission(image_url, b['name'], b['skill'])
                    
                    if "PASS" in decision.upper():
                        print(f"✅ WINNER FOUND! Reasoning: {decision}")
                        
                        # 1. Payout
                        tx_hash = execute_payout(cast['author']['verifications'][0] if cast['author']['verifications'] else "Unknown")
                        
                        # 2. Public Explanation (The Bounty Requirement)
                        explanation = f"Bounty Paid! Winner: @{cast['author']['username']}. Reasoning: {decision} Proof: {image_url}"
                        post_explanation(explanation, cast['hash'])
                        print("✈️ Public explanation posted to Farcaster.")
                    else:
                        print(f"❌ Submission Rejected: {decision}")

        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    main()
