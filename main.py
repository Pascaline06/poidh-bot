import os
from web3 import Web3

RPC_URL = os.getenv("BASE_RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# DATA FROM BASESCAN LOG
TARGET_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
ON_CHAIN_ID = 136 # The real ID for web 1122
START_BLOCK = 44235945 

def final_pull():
    print(f"--- RUN #132: PULLING CLAIMS FOR ON-CHAIN ID {ON_CHAIN_ID} ---")
    
    # Format the ID for Topic 3 (indexed uint256)
    hex_id = hex(ON_CHAIN_ID)[2:].zfill(64)
    topic_id = f"0x{hex_id}"
    
    logs = w3.eth.get_logs({
        "fromBlock": START_BLOCK,
        "toBlock": "latest",
        "address": w3.to_checksum_address(TARGET_CA),
        "topics": [EVENT_SIG, None, None, topic_id]
    })
    
    print(f"Success! Found {len(logs)} claims on-chain.")
    for log in logs:
        print(f"Tx: {log['transactionHash'].hex()}")

if __name__ == "__main__":
    final_pull()
