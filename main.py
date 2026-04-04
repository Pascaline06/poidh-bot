import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# This is the block where we KNOW Bounty 136 was born
BIRTH_BLOCK = 44235945 

def find_correct_contract():
    print("--- RUN #119: CONTRACT IDENTIFIER ---")
    try:
        # We fetch the block and all its transactions
        block = w3.eth.get_block(BIRTH_BLOCK, full_transactions=True)
        print(f"Searching {len(block.transactions)} transactions in block {BIRTH_BLOCK}...")
        
        found_addresses = set()
        for tx in block.transactions:
            # We look for transactions sent to a contract that might be POIDH
            if tx['to']:
                found_addresses.add(tx['to'])
        
        print("\n[!] The claims are happening on ONE of these addresses:")
        for addr in found_addresses:
            # We check if this address had a 'Bounty 136' event in that block
            logs = w3.eth.get_logs({
                "fromBlock": BIRTH_BLOCK,
                "toBlock": BIRTH_BLOCK,
                "address": addr
            })
            if logs:
                print(f"FOUND ACTIVE CONTRACT: {addr}")
                print(f"Confirming... Found {len(logs)} events in this block.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_correct_contract()
