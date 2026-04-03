# 🤖 Autonomous POIDH Agent

This bot uses **Google Gemini 1.5 Flash** to autonomously verify real-world tasks on Farcaster and execute payouts via the **POIDH Smart Contract** on Base.

### 🏗 Architecture
1. **Detection**: Monitors Farcaster replies using Neynar API.
2. **Evaluation**: Gemini Vision analyzes images to distinguish between digital fraud and real-world physical proof.
3. **Execution**: Deterministic payout logic triggers the `payout` function on the POIDH contract.

### ⚙️ Setup
1. **GitHub Secrets**: Add `GEMINI_API_KEY`, `NEYNAR_API_KEY`, `BASE_RPC_URL`, and `BOT_PRIVATE_KEY`.
2. **Workflow**: The bot is scheduled via GitHub Actions to run every hour.

### 🛡 Autonomy & Constraints
- **Self-Enforcement**: The bot only pays if Gemini returns a "YES" token.
- **Limitations**: Currently requires a manual one-time bounty creation on poidh.xyz to save on gas during the trial phase.
