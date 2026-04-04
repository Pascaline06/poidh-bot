from web3 import Web3
from eth_abi import decode

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT_ADDR = "0x5555Fa783936C260f77385b4E153B9725feF1719"
CLAIM_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_ID = 136
START_BLOCK = 44222459 

# The "Blueprint" for the ClaimCreated event data
# Based on the POIDH contract structure
EVENT_TYPES = ['string', 'uint256', 'uint256'] # title, amount, createdAt

def fetch_and_analyze():
    if not w3.is_connected(): return
    latest = w3.eth.block_number
    print(f"--- ANALYZING SUBMISSIONS FOR BOUNTY {TARGET_ID} ---")

    # Scanning from the creation block to now
    logs = w3.eth.get_logs({
        "fromBlock": START_BLOCK,
        "toBlock": latest,
        "address": w3.to_checksum_address(CONTRACT_ADDR),
        "topics": [CLAIM_SIG]
    })

    found_count = 0
    for log in logs:
        # Check if Topic 3 matches Bounty 136
        if int(log['topics'][3].hex(), 16) == TARGET_ID:
            found_count += 1
            claimer = "0x" + log['topics'][2].hex()[-40:]
            tx_hash = log['transactionHash'].hex()
            
            # DECODING THE DESCRIPTION
            # We use eth_abi to pull the actual string out of the hex data
            raw_data = bytes.fromhex(log['data'].hex()[2:])
            try:
                # POIDH stores the submission text as the first string in the data
                decoded = decode(['string'], raw_data[64:])[0] 
            except:
                # Fallback: Just try to strip the hex if ABI decoding fails
                decoded = w3.to_text(log['data']).strip()

            print(f"\n[ SUBMISSION #{found_count} ]")
            print(f"User: {claimer}")
            print(f"Content: {decoded}")
            print(f"Verify: https://basescan.org/tx/{tx_hash}")

    if found_count == 0:
        print("No claims found in this range. Try increasing START_BLOCK.")

if __name__ == "__main__":
    fetch_and_analyze()
