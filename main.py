import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# We will check the two most likely contract addresses
CONTRACT_A = "0x5555Fa783936C260f77385b4e153B9725fef1719"
CONTRACT_B = "0xB50D064fde85392D66649fD04E85C93683fba2B3"

def discovery_scan():
    print("--- RUN #117: DISCOVERY MODE ---")
    current_block = w3.eth.block_number
    # Scan the last 2000 blocks (~1 hour of activity)
    start_block = current_block - 2000
    
    for addr in [CONTRACT_A, CONTRACT_B]:
        print(f"\nChecking Address: {addr}")
        try:
            logs = w3.eth.get_logs({
                "fromBlock": start_block,
                "toBlock": "latest",
                "address": w3.to_checksum_address(addr)
            })
            
            if not logs:
                print("  > No activity found on this contract in the last hour.")
                continue
                
            print(f"  > Found {len(logs)} recent events. Listing IDs found:")
            found_ids = set()
            for log in logs:
                # Most POIDH events put the Bounty ID in the second topic (index 1)
                if len(log['topics']) > 1:
                    b_id = int(log['topics'][1].hex(), 16)
                    found_ids.add(b_id)
            
            print(f"  > Bounty IDs active right now: {sorted(list(found_ids))}")
            
        except Exception as e:
            print(f"  > Error scanning {addr[:10]}: {e}")

if __name__ == "__main__":
    discovery_scan()
