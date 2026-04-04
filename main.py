import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
TARGET_ID = 136

def get_bounty_id_at_block(block_num):
    """Checks the contract's bounty counter at a specific point in history."""
    # This calls the 'bountyCount' or similar public variable on the contract
    # If your contract uses a different getter, we adjust this line
    try:
        # Most POIDH-style contracts have a bountyCount() function
        count_hex = w3.eth.call({
            'to': w3.to_checksum_address(CONTRACT_ADDR),
            'data': '0x3497793e' # Selector for bountyCount()
        }, block_num)
        return int(count_hex.hex(), 16)
    except:
        return None

def binary_search_block():
    print(f"Targeting Bounty {TARGET_ID}. Finding exact block via Binary Search...")
    
    # Range: From contract deployment (~40m) to your last seen block
    low = 40000000 
    high = 44235945 
    found_block = high

    while low <= high:
        mid = (low + high) // 2
        current_id = get_bounty_id_at_block(mid)
        
        if current_id is None: # Block might be too old for some RPCs
            low = mid + 1
            continue

        if current_id >= TARGET_ID:
            found_block = mid
            high = mid - 1
        else:
            low = mid + 1
            
    print(f"\n[!!!] FOUND IT: Bounty 136 first appeared in Block: {found_block}")
    print("Now we can scan JUST that block area for the claim images.")

if __name__ == "__main__":
    binary_search_block()
