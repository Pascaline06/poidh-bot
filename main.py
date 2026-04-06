import os
import json
import requests
from web3 import Web3

# --- CONFIGURATION ---
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 136
STATE_FILE = "last_seen_id.json"

ABI = [{ "inputs": [ {"internalType": "uint256", "name": "_bountyId", "type": "uint256"}, {"internalType": "uint256", "name": "_offset", "type": "uint256"} ], "name": "getClaimsByBountyId", "outputs": [ { "components": [ {"internalType": "uint256", "name": "id", "type": "uint256"}, {"internalType": "address", "name": "issuer", "type": "address"}, {"internalType": "uint256", "name": "bountyId", "type": "uint256"}, {"internalType": "address", "name": "bountyIssuer", "type": "address"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "string", "name": "description", "type": "string"}, {"internalType": "uint256", "name": "createdAt", "type": "uint256"}, {"internalType": "bool", "name": "accepted", "type": "bool"} ], "internalType": "struct POIDH.Claim[]", "name": "", "type": "tuple[]" } ], "stateMutability": "view", "type": "function" }]

# --- THE BRAIN (Gemini Free Tier) ---
def evaluate_claims_with_ai(new_claims):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Gemini API Key missing. Skipping evaluation.")
        return None

    claims_data = ""
    for c in new_claims:
        claims_data += f"- ID {c[0]}: Title '{c[4]}', Description: '{c[5]}'\n"

    print(f"🧠 Sending {len(new_claims)} claims to the Gemini Brain...")

    prompt = (
        f"You are the autonomous judge for POIDH Bounty #{BOUNTY_ID}: 'Holding a Physical Book'.\n"
        "Your goal is to pick the most authentic and descriptive submission.\n\n"
        "Submissions:\n" + claims_data + "\n"
        "Pick exactly ONE winner. Respond ONLY with a JSON object exactly like this:\n"
        '{"winner_id": 123, "reasoning": "A 1-2 sentence explanation of why this won."}'
    )

    try:
        # Hitting the free Gemini 2.5 Flash endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0, # Keeps the AI perfectly logical
                "responseMimeType": "application/json" # Forces strict JSON output
            }
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        res_json = response.json()
        
        # Debugger to catch API errors
        if 'candidates' not in res_json:
            print(f"❌ Gemini API Error: {json.dumps(res_json, indent=2)}")
            return None
            
        content = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        decision = json.loads(content)
        
        print(f"🏆 AI DECISION: Claim #{decision['winner_id']} wins!")
        print(f"📝 REASONING: {decision['reasoning']}")
        return decision

    except Exception as e:
        print(f"❌ Brain Error: {e}")
        return None

# --- MAIN AUTOMATION ---
def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    
    last_seen = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_seen = json.load(f).get("last_id", 0)

    print(f"📡 Checking for claims newer than ID {last_seen}...")
    all_claims = contract.functions.getClaimsByBountyId(BOUNTY_ID, 0).call()
    
    new_claims = [c for c in all_claims if c[0] > last_seen and c[7] == False]

    if not new_claims:
        print("😴 No new submissions to judge.")
        return

    decision = evaluate_claims_with_ai(new_claims)

    if decision:
        new_last_id = max(c[0] for c in new_claims)
        with open(STATE_FILE, "w") as f:
            json.dump({"last_id": new_last_id}, f)
        print(f"💾 State updated to ID {new_last_id}")

if __name__ == "__main__":
    run_bot()
