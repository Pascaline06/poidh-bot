from web3 import Web3
import eth_utils

# 1. SETUP
RPC_URL = "https://mainnet.base.org"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT_ADDR = "0x5555Fa783936C260f77385b4E153B9725feF1719"
CLAIM_CREATED_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_BOUNTY_ID = 136
START_BLOCK = 44222459 

def decode_and_judge():
    if not w3.is_connected(): return
    print(f"--- FETCHING AND DECODING CLAIMS FOR BOUNTY {TARGET_BOUNTY_ID} ---")

    logs = w3.eth.get_logs({
        "fromBlock": START_BLOCK,
        "toBlock": START_BLOCK + 5000,
        "address": w3.to_checksum_address(CONTRACT_ADDR),
        "topics": [CLAIM_CREATED_SIG] 
    })

    for log in logs:
        if int(log['topics'][3].hex(), 16) == TARGET_BOUNTY_ID:
            claimer = "0x" + log['topics'][2].hex()[-40:]
            tx_hash = log['transactionHash'].hex()
            
            # DECODING THE HEX DATA
            # The description usually starts after the standard parameters
            raw_data = log['data'].hex()
            try:
                # Basic cleanup: remove prefix and decode as UTF-8
                # This grabs the text content hidden in the transaction data
                decoded_text = bytes.fromhex(raw_data.replace('0x', '')).decode('utf-8', errors='ignore')
            except:
                decoded_text = "Could not decode text"
            
            print(f"\n--- [ CLAIM FOUND ] ---")
            print(f"Submitter: {claimer}")
            print(f"Description: {decoded_text}")
            print(f"Link: https://basescan.org/tx/{tx_hash}")

if __name__ == "__main__":
    decode_and_judge()
