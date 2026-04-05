import os
import json
import requests
from web3 import Web3

# --- CONFIG ---
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 136
STATE_FILE = "last_seen_id.json"
NTFY_TOPIC = "poidh_bounty_alerts_123"

ABI = [{ "inputs": [ {"internalType": "uint256", "name": "_bountyId", "type": "uint256"}, {"internalType": "uint256", "name": "_offset", "type": "uint256"} ], "name": "getClaimsByBountyId", "outputs": [ { "components": [ {"internalType": "uint256", "name": "id", "type": "uint256"}, {"internalType": "address", "name": "issuer", "type": "address"}, {"internalType": "uint256", "name": "bountyId", "type": "uint256"}, {"internalType": "address", "name": "bountyIssuer", "type": "address"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "string", "name": "description", "type": "string"}, {"internalType": "uint256", "name": "createdAt", "type": "uint256"}, {"internalType": "bool", "name": "accepted", "type": "bool"} ], "internalType": "struct POIDH.Claim[]", "name": "", "type": "tuple[]" } ], "stateMutability": "view", "type": "function" }]

def send_notification(claim_id, user, title):
    bounty_link = f"https://poidh.xyz/bounty/{BOUNTY_ID}"
    msg = f"New Submission #{claim_id} for Physical Book Bounty!\nFrom: {user[:8]}...\nTitle: {title}"
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                      data=msg.encode('utf-8'),
                      headers={"Title": "🎁 POIDH New Claim!", "Click": bounty_link, "Priority": "high", "Tags": "books,star2"})
    except Exception as e:
        pass # Stay quiet on error

# --- THE BRAIN ---
def evaluate_claims_with_ai(claims_list):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY missing from GitHub Secrets. Skipping AI Brain.")
        return None

    print("\n🧠 Waking up the AI Brain to evaluate submissions...")
    
    prompt = "You are an impartial AI judge for a photo contest called 'B01: Holding a Physical Book'.\n"
    prompt += "Review these submissions. Pick the most creative, fitting, or genuine one.\n\n"
    
    for c in claims_list:
        prompt += f"Submission ID: {c[0]} | Title: {c[4]} | Details: {c[5]}\n"
    
    prompt += "\nRespond ONLY in valid JSON format exactly like this, with no extra text:\n"
    prompt += '{"winner_id": 123, "reasoning": "A concise 2-sentence explanation of why this won."}'

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2 # Low temperature keeps the AI logical and strict
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Strip markdown formatting just in case the AI adds it
        content = content.replace('```json', '').replace('```', '').strip()
        decision = json.loads(content)
        
        print(f"\n🏆 AI DECISION: Submission #{decision['winner_id']} wins!")
        print(f"🗣️ AI REASONING: {decision['reasoning']}\n")
        
        return decision
    except Exception as e:
        print(f"❌ AI Evaluation failed: {e}")
        return None

def load_last_id():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("last_id", 0)
    return 0

def save_last_id(last_id):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_id": last_id}, f)

def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    last_seen_id = load_last_id()

    try:
        print(f"📡 Checking Bounty 136 for claims higher than {last_seen_id}...")
        claims = contract.functions.getClaimsByBountyId(BOUNTY_ID, 0).call()
        
        new_claims = [c for c in claims if c[0] > last_seen_id]
        
        if not new_claims:
            print("😴 Nothing new.")
            return

        highest_id = last_seen_id
        for c in new_claims:
            print(f"🌟 Found Claim #{c[0]}: {c[4]}")
            send_notification(c[0], c[1], c[4])
            if c[0] > highest_id:
                highest_id = c[0]

        # Trigger the AI evaluation on the new batch of claims
        if len(new_claims) > 0:
            ai_decision = evaluate_claims_with_ai(new_claims)
            
            if ai_decision:
                # Placeholder for Phase 2: The Hands (On-Chain Execution)
                print(f"⚙️ [Phase 2 Placeholder]: I would now execute an on-chain transaction to pay out Claim {ai_decision['winner_id']}")

        save_last_id(highest_id)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_bot()
