import os
import json
from web3 import Web3
from google import genai

# Config
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 1122
STATE_FILE = "state.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def load_block():
    try:
        with open(STATE_FILE, "r") as f:
            return int(json.load(f)["last_block"])
    except:
        return 44100000

def save_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": int(block)}, f)

def run_bot():
    if not w3.is_connected():
        print("❌ Connection failed")
        return

    start = load_block()
    current_chain = w3.eth.block_number
    # Ultra-safe 500 block range to avoid Alchemy 400 errors
    end = min(start + 500, current_chain)
    
    print(f"📡 Scanning {start} to {end}...")

    # Alchemy/Base requires HEX strings for block numbers
    params = {
        "fromBlock": Web3.to_hex(start),
        "toBlock": Web3.to_hex(end),
        "address": w3.to_checksum_address(POIDH_CA),
        "topics": [EVENT_SIG, Web3.to_hex(BOUNTY_ID).rjust(66, '0'), None, None]
    }

    try:
        logs = w3.eth.get_logs(params)
        for log in logs:
            tx = log["transactionHash"].hex()
            print(f"✨ Claim found: https://basescan.org/tx/{tx}")
        
        save_block(end + 1)
        print(f"✅ Success. Next start: {end + 1}")
    except Exception as e:
        print(f"❌ Alchemy rejected the request: {e}")

if __name__ == "__main__":
    run_bot()
