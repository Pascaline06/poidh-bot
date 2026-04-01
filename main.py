import os
import google.generativeai as genai
from pinata_fdk import PinataFDK

# 1. Setup the "Locker" Keys
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
fdk = PinataFDK(
    pinata_jwt=os.getenv("PINATA_JWT"),
    pinata_gateway=os.getenv("PINATA_GATEWAY"),
    app_fid=os.getenv("APP_FID"),
    app_mnemonic=os.getenv("FARCASTER_DEVELOPER_MNEMONIC")
)

# 2. Setup the AI "Vision"
model = genai.GenerativeModel('gemini-1.5-flash')

def verify_beverage(image_url):
    prompt = "Is there a drink/beverage in this image? Answer with only 'YES' or 'NO'."
    # In a real bot, we'd download the image and send it to Gemini here
    # For now, we'll return YES to test the flow
    return "YES"

def main():
    print("Bot is starting... checking for beverage bounties!")
    # The bot will loop through mentions here using Pinata
    # (Simplified for your first run)
    print("Search complete. No new mentions found.")

if __name__ == "__main__":
    main()
