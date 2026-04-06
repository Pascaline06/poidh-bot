# 🤖 Poidh Aegis Bot Judge: Autonomous AI Bounty Warden

Most bounty bots are easily fooled. **Poidh Aegis** is different. It’s an autonomous agent designed to judge, verify, and pay out bounties on **Base** without needing a human to babysit the "Accept" button.

---

## ⚖️ Why use Aegis?

* **It’s Not Easily Tricked:** While other bots just read descriptions, Aegis uses a "Visual-to-Text Audit." It can tell the difference between a high-quality submission and someone trying to cheese the system with a "hand-only" photo.
* **Built-in Gas Efficiency:** We solved the common "Base L2 Gas Estimation" bug by hardcoding safe limits, so the bot never gets stuck in a loop of failed transactions.
* **Protocol-Safe:** It checks the smart contract state *before* it tries to pay. If a bounty is already closed, Aegis moves on. Your funds stay exactly where they belong.
* **Farcaster Ready:** It generates protocol-ready announcements, making it easy to keep the community updated on who won and why.

---

## ⚙️ Tech Stack

- **Reasoning:** Gemini 3 Flash (The "Brain")
- **Blockchain:** Web3.py on Base Mainnet (The "Hand")
- **Automation:** GitHub Actions (The "Heart")
- **Social:** Farcaster/Neynar-ready logic (The "Voice")

---

## 🚀 How to Set Up

1.  **Repo Setup:** Fork this repository.
2.  **Secret Keys:** Add your `ALCHEMY_KEY`, `GEMINI_API_KEY`, and `BOT_PRIVATE_KEY` to your GitHub Secrets.
3.  **Identity:** Add your `FARCASTER_ID` so the bot knows who it's representing.
4.  **Run:** Trigger the workflow and watch the AI Judge go to work.

---

> **Dev Note:** This project was built to be "PC-Optional." It runs entirely in a serverless environment, managed 100% from a mobile device.
