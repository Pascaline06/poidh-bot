import os
import json
import requests
from web3 import Web3

# --- CONFIGURATION ---
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
BOUNTY_ID = 136
STATE_FILE = "last_seen_id.json"

# ABI for reading claims
ABI = [{ "inputs": [ {"internalType": "uint256", "name": "_bountyId", "type": "uint256"}, {"internalType": "uint256", "name": "_offset", "type": "uint256"} ], "name": "getClaimsByBountyId", "outputs": [ { "components": [ {"internalType": "uint256", "name": "id", "type": "uint256"}, {"internalType": "address", "name": "issuer", "type": "address"}, {"internalType": "uint256", "name": "bountyId", "type": "uint256"}, {"internalType": "address", "name": "bountyIssuer", "type": "address"}, {"internalType": "string", "name": "name", "type": "string"}, {"internalType": "string", "name": "description", "type": "string"}, {"internalType": "uint256", "name": "createdAt", "type": "uint256"}, {"internalType": "bool", "name": "accepted", "type": "bool"} ], "internalType": "struct POIDH.Claim[]", "name": "", "type": "tuple[]" } ], "stateMutability": "view", "type": "function" }]

# --- THE BRAIN (Evaluation Logic) ---
def evaluate_claims_with_ai(new_claims):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ AI Key missing. Skipping evaluation.")
        return None

    claims_data = ""
    for c in new_claims:
        claims_data += f"- ID {c[0]}: Title '{c[4]}', Description: '{c[5]}'\n"

    print(f"🧠 Sending {len(new_claims)} claims to the AI Brain...")

    prompt = (
        f"You are the autonomous judge for POIDH Bounty #{BOUNTY_ID}: 'Holding a Physical Book'.\n"
        "Pick exactly ONE winner. Respond ONLY with a JSON object:\n"
        '{"winner_id": ID_NUMBER, "reasoning": "A 1-2 sentence explanation of why this won."}'
    )

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": "You are a deterministic judge."},
                             {"role": "user", "content": prompt}],
                "temperature": 0
            }
        )
        
        res_json = response.json()

        # --- DEBUGGER: If there's no 'choices', show us the REAL error ---
        if 'choices' not in res_json:
            print(f"❌ OpenAI API Error: {json.dumps(res_json, indent=2)}")
            return None
        
        content = res_json['choices'][0]['message']['content'].strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
            
        decision = json.loads(content)
        print(f"🏆 AI DECISION: Claim #{decision['winner_id']} wins!")
        return decision

    except Exception as e:
        print(f"❌ Brain Error: {e}")
        return None
# --- MAIN AUTOMATION ---
def run_bot():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract = w3.eth.contract(address=w3.to_checksum_address(POIDH_CA), abi=ABI)
    
    # Load memory
    last_seen = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_seen = json.load(f).get("last_id", 0)

    print(f"📡 Checking for claims newer than ID {last_seen}...")
    all_claims = contract.functions.getClaimsByBountyId(BOUNTY_ID, 0).call()
    
    # Filter for new, unaccepted claims
    new_claims = [c for c in all_claims if c[0] > last_seen and c[7] == False]

    if not new_claims:
        print("😴 No new submissions to judge.")
        return

    # Phase 1: Evaluate
    decision = evaluate_claims_with_ai(new_claims)

    if decision:
        # Save progress so we don't judge the same ones twice
        new_last_id = max(c[0] for c in new_claims)
        with open(STATE_FILE, "w") as f:
            json.dump({"last_id": new_last_id}, f)
        print(f"💾 State updated to ID {new_last_id}")

if __name__ == "__main__":
    run_bot()
