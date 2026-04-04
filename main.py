from web3 import Web3

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT_ADDR = "0x5555Fa783936C260f77385b4E153B9725feF1719"
# The language for "Claims"
CLAIM_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_ID = 136
# Start exactly where your bounty creation TX was found
START_BLOCK = 44222459 

def fetch_all_claims():
    if not w3.is_connected(): return
    
    # Get the LATEST block on the network right now
    latest_block = w3.eth.block_number
    print(f"--- SCANNING FROM {START_BLOCK} TO CURRENT {latest_block} ---")

    # Use a loop to avoid "Too many results" errors
    current_start = START_BLOCK
    step = 2000 # Scan in chunks of 2000 blocks

    while current_start < latest_block:
        current_end = min(current_start + step, latest_block)
        print(f"Checking blocks {current_start} to {current_end}...")
        
        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(CONTRACT_ADDR),
                "topics": [CLAIM_SIG]
            })

            for log in logs:
                # ClaimCreated stores Bounty ID in Topic 3
                if int(log['topics'][3].hex(), 16) == TARGET_ID:
                    claimer = "0x" + log['topics'][2].hex()[-40:]
                    tx_hash = log['transactionHash'].hex()
                    
                    # Decoding the Description
                    raw_data = log['data'].hex()
                    try:
                        # Extract the hex and decode it
                        decoded = bytes.fromhex(raw_data.replace('0x', '')).decode('utf-8', errors='ignore')
                    except:
                        decoded = "[Raw Data Found but could not decode]"

                    print(f"\n✅ CLAIM DETECTED!")
                    print(f"Submitter: {claimer}")
                    print(f"Text: {decoded}")
                    print(f"Basescan: https://basescan.org/tx/{tx_hash}")

        except Exception as e:
            print(f"⚠️ Chunk Error: {e}")
            
        current_start = current_end + 1

if __name__ == "__main__":
    fetch_all_claims()
