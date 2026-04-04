from web3 import Web3

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT = "0x5555Fa783936C260f77385b4E153B9725feF1719"

# SIGNATURES
BOUNTY_SIG = "0xd265c5d6a9224c4853317e9e3262b0605b45f0e87c8bfd17d020e54a87c439af"
CLAIM_SIG  = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"

# THE TARGET BLOCK (From your Basescan screenshot)
TARGET_BLOCK = 44222459 

def trace_and_judge():
    if not w3.is_connected(): return
    print(f"--- ANALYZING BLOCK {TARGET_BLOCK} ---")

    # Fetch EVERYTHING for this contract in that block
    logs = w3.eth.get_logs({
        "fromBlock": TARGET_BLOCK,
        "toBlock": TARGET_BLOCK,
        "address": w3.to_checksum_address(CONTRACT)
    })

    print(f"Found {len(logs)} total events. Sorting...")

    for log in logs:
        sig = log['topics'][0].hex()
        
        # IF IT'S A BOUNTY CREATION
        if sig == BOUNTY_SIG:
            b_id = int(log['topics'][1].hex(), 16)
            print(f"\n[NEW BOUNTY] ID: {b_id} | TX: {log['transactionHash'].hex()}")
            
        # IF IT'S A CLAIM SUBMISSION
        elif sig == CLAIM_SIG:
            b_id = int(log['topics'][3].hex(), 16)
            claimer = "0x" + log['topics'][2].hex()[-40:]
            print(f"\n[NEW CLAIM] For Bounty: {b_id}")
            print(f"  From Submitter: {claimer}")
            print(f"  Evidence TX: https://basescan.org/tx/{log['transactionHash'].hex()}")

if __name__ == "__main__":
    trace_and_judge()
