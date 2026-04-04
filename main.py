import time
import os
from web3 import Web3

# =========================
# CONFIG
# =========================
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"

# Event signature (keep this)
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"

CHUNK_SIZE = 500

w3 = Web3(Web3.HTTPProvider(RPC_URL))


# =========================
# MAIN BOT
# =========================
def run_bot():
    print("🤖 Starting bot run...", flush=True)

    # Check connection
    if not w3.is_connected():
        print("❌ RPC connection failed", flush=True)
        return

    latest_block = w3.eth.block_number
    start_block = latest_block - 3000  # scan recent blocks only

    print(f"🔍 Scanning blocks {start_block} → {latest_block}", flush=True)

    current_start = start_block
    total_logs = 0

    while current_start <= latest_block:
        current_end = min(current_start + CHUNK_SIZE, latest_block)

        print(f"➡️ Chunk: {current_start} → {current_end}", flush=True)

        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG]  # ONLY event signature (no filters)
            })

            if logs:
                print(f"🔥 Found {len(logs)} logs", flush=True)

            for log in logs:
                print("\n📦 RAW LOG:", log, flush=True)
                total_logs += 1

        except Exception as e:
            print(f"⚠️ Error at {current_start}: {e}", flush=True)
            time.sleep(2)

        current_start = current_end + 1
        time.sleep(1)

    print(f"\n✅ Scan complete. Total logs: {total_logs}", flush=True)
    print("🏁 Bot run finished.", flush=True)


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_bot()
