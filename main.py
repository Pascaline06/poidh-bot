import os
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# The contract address from your original code
CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"

def discover_event_names():
    print(f"🕵️ Analyzing contract {CONTRACT_ADDR} for hidden events...")
    try:
        current_block = w3.eth.block_number
        # Scan last 2000 blocks for ANY activity on this specific address
        logs = w3.eth.get_logs({
            "fromBlock": current_block - 2000,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR)
        })

        if not logs:
            print("❌ No activity found on this address in the last 2000 blocks.")
            print("This usually means the contract address itself is wrong.")
            return

        print(f"✅ Found {len(logs)} interactions! Extracting event signatures...")
        
        signatures = set()
        for log in logs:
            # The first topic [0] is the hashed name of the event
            signatures.add(log['topics'][0].hex())
        
        print("\n--- Detected Event Signatures (Topics) ---")
        for sig in signatures:
            print(f"🔹 {sig}")
            
        print("\nNext step: I will decode these signatures to find the new 'Claim' event name.")

    except Exception as e:
        print(f"❌ Error during discovery: {e}")

if __name__ == "__main__":
    discover_event_names()
