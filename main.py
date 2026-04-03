import os
import requests
import base64
from web3 import Web3

# --- CONFIG ---
RPC_URL = os.getenv("BASE_RPC_URL")
API_KEY = os.getenv("GEMINI_API_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDR = "0x5555fa783936c260f77385b4e153b9725fef1719"
CLAIM_TOPIC = "0x8e899c06f3271c67860e48d8347164d6a78655c6be9fcfaa86f714cc7d074c78"
TARGET_IDS = [705, 706]

def analyze_with_gemini(img_url):
    """Bypasses restricted gateways and sends image to Gemini 3.1 Flash Lite."""
    # Using v1beta and the 3.1 Lite model shown in your AI Studio
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={API_KEY}"
    
    # FIX: Use official ipfs.io gateway to resolve DNS and bypass Pinata restrictions
    if "/ipfs/" in img_url:
        cid = img_url.split("/ipfs/")[-1]
        img_url = f"https://ipfs.io/ipfs/{cid}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        # 1. Download image
        img_response = requests.get(img_url, headers=headers, timeout=15)
        img_response.raise_for_status()
        
        # 2. Convert to Base64
        img_b64 = base64.b64encode(img_response.content).decode('utf-8')
        
        # 3. Request
