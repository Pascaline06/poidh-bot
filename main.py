import os
import requests
import base64
import re
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDR = "0x5555Fa783936C260f77385b4e153B9725fef1719"
TARGET_ID = 136
# Start just before the birth block we found
START_BLOCK = 44235900 

def get_pure_image(blob):
    matches = re.findall(r'(Qm[1-9A-HJ-NP-Za-km-z]{44}|bafy[a-zA-Z0-9]{55}|https?://[^\s<>"]+|ipfs://[^\s<>"]+)', blob)
    if not matches: return None, None
    cid = matches[0].split("/ipfs/")[-1].replace("ipfs://", "").split("?")[0].strip()
    
    # Using more gateways to ensure we don't miss the 6 claims
    gateways = [
        f"https://poidh.xyz/api/ipfs/{cid}",
        f"https://gateway.pinata.cloud/ipfs/{cid}",
        f"https://ipfs.io/ipfs/{cid}",
        f"https://cloudflare-ipfs.com/ipfs/{cid}"
    ]
    for url in gateways:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200: return res.content, matches[0]
        except: continue
    return None, None

def run_deep_state_scan():
    print(f"--- RUN #115: UNFILTERED SEARCH FOR 6 CLAIMS ---")
    current_block = w3.eth.block_number
    target_hex_fragment = hex(TARGET_ID)[2:].zfill(2) # Looking for '88' (136 in hex)
    
    try:
        # We fetch ALL logs from the contract, no filters, to see why we missed them
        logs = w3.eth.get_logs({
            "fromBlock": START_BLOCK,
            "toBlock": current_block,
            "address": w3.to_checksum_address(CONTRACT_ADDR)
        })

        found_count = 0
        print(f"Total contract events in range: {len(logs)}")
        
        for log in logs:
            # Check if the target ID (136) appears anywhere in the data or topics
            log_data_hex = log['data'].hex()
            topics_hex = "".join([t.hex() for t in log['topics']])
            
            if target_hex_fragment in log_data_hex or target_hex_fragment in topics_hex:
                found_count += 1
                print(f"[!] POTENTIAL MATCH {found_count}: Block {log['blockNumber']}")
                
                # Try to extract image
                raw_text = bytes.fromhex(log_data_hex).decode('utf-8', 'ignore')
                img_bytes, path = get_pure_image(raw_text)
                
                if img_bytes:
                    print(f"[*] Found image! Sending to AI...")
                    # Insert AI judge call here as needed
                else:
                    print(f"[?] Event found but no IPFS link in data.")

        if found_count == 0:
            print("[X] Still 0 found. Double-check if the contract address is correct.")

    except Exception as e:
        print(f"Scan failed: {e}")

if __name__ == "__main__":
    run_deep_state_scan()
