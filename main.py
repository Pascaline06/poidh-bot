import time
import json
from web3 import Web3

# =========================
# CONFIG
# =========================
RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_KEY')}"  # CHANGE THIS
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

CHUNK_SIZE = 500
STATE_FILE = "state.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))


# =========================
# STATE MANAGEMENT
# =========================
def load_last_block():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)["last_block"]
    except:
        return None


def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)


# =========================
# MAIN BOT LOGIC
# =========================
def run_bot():
    print("🤖 Starting bot run...", flush=True)

    if not w3.is_connected():
        print("❌ RPC connection failed", flush=True)
        return

    latest_block = w3.eth.block_number
    last_block = load_last_block()

    # First run fallback
    if last_block is None:
        last_block = latest_block - 3000
        print(f"⚠️ No state found. Starting from {last_block}", flush=True)

    print(f"🔍 Scanning blocks {last_block} → {latest_block}", flush=True)

    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)

    current_start = last_block
    total_matches = 0

    while current_start <= latest_block:
        current_end = min(current_start + CHUNK_SIZE, latest_block)

        print(f"➡️ Chunk: {current_start} → {current_end}", flush=True)

        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG, None, None, topic_id]
            })

            if logs:
                print(f"🔥 Found {len(logs)} matches!", flush=True)

            for log in logs:
                tx_hash = log["transactionHash"].hex()
                block_number = log["blockNumber"]

                print(f"\n✅ MATCH FOUND", flush=True)
                print(f"Block: {block_number}", flush=True)
                print(f"TX: https://basescan.org/tx/{tx_hash}", flush=True)

                total_matches += 1

                # 👉 NEXT STEP: evaluation logic goes here

        except Exception as e:
            print(f"⚠️ Error at {current_start}: {e}", flush=True)

            if "429" in str(e):
                print("⏳ Rate limited. Sleeping 5s...", flush=True)
                time.sleep(5)
            else:
                time.sleep(2)

        save_last_block(current_end)
        current_start = current_end + 1
        time.sleep(1)

    print(f"\n✅ Scan complete. Total matches: {total_matches}", flush=True)
    print("🏁 Bot run finished.", flush=True)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_bot()
