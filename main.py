import time
import json
from web3 import Web3

# =========================
# CONFIG
# =========================
RPC_URL = "https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY"  # <-- CHANGE THIS
POIDH_CA = "0x5555Fa783936C260f77385b4E153B9725feF1719"
EVENT_SIG = "0x8e099c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
BOUNTY_ID = 136

CHUNK_SIZE = 500
SLEEP_BETWEEN_REQUESTS = 2
LOOP_DELAY = 30

STATE_FILE = "state.json"

w3 = Web3(Web3.HTTPProvider(RPC_URL))


# =========================
# STATE MANAGEMENT
# =========================
def load_last_block():
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_block", None)
    except:
        return None


def save_last_block(block):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_block": block}, f)


# =========================
# MAIN SCAN FUNCTION
# =========================
def scan_for_claims():
    if not w3.is_connected():
        print("❌ Not connected to RPC")
        return

    latest_block = w3.eth.block_number

    last_block = load_last_block()

    # First run fallback
    if last_block is None:
        print("⚠️ No previous state found. Starting from recent blocks...")
        last_block = latest_block - 5000  # safe fallback

    print(f"\n🔍 Scanning from {last_block} → {latest_block}")

    # Format bountyId for topic
    topic_id = "0x" + hex(BOUNTY_ID)[2:].zfill(64)

    current_start = last_block

    while current_start <= latest_block:
        current_end = min(current_start + CHUNK_SIZE, latest_block)

        try:
            logs = w3.eth.get_logs({
                "fromBlock": current_start,
                "toBlock": current_end,
                "address": w3.to_checksum_address(POIDH_CA),
                "topics": [EVENT_SIG, None, None, topic_id]
            })

            if logs:
                print(f"\n🔥 Found {len(logs)} matching logs between {current_start}-{current_end}")

            for log in logs:
                tx_hash = log['transactionHash'].hex()
                block_number = log['blockNumber']

                print(f"\n✅ MATCH FOUND")
                print(f"Block: {block_number}")
                print(f"TX: https://basescan.org/tx/{tx_hash}")

                # 👉 THIS IS WHERE YOU LATER ADD:
                # - Store submission
                # - Evaluate
                # - Pick winner

        except Exception as e:
            print(f"⚠️ Error at block {current_start}: {e}")

            # Handle rate limit gracefully
            if "429" in str(e):
                print("⏳ Rate limited. Sleeping longer...")
                time.sleep(5)
            else:
                time.sleep(2)

        # Save progress
        save_last_block(current_end)

        current_start = current_end + 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print("✅ Scan cycle complete")


# =========================
# BOT LOOP (AUTONOMY)
# =========================
def run_bot():
    print("🤖 Bot started...")

    while True:
        try:
            scan_for_claims()
            print(f"😴 Sleeping {LOOP_DELAY}s before next scan...\n")
            time.sleep(LOOP_DELAY)

        except Exception as e:
            print(f"❌ Critical error: {e}")
            time.sleep(10)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_bot()
