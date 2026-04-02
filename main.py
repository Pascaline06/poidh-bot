import os
import json
import requests
from google import genai

# Setup
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
NEYNAR_API_KEY = os.getenv("NEYNAR_API_KEY")
PINATA_JWT = os.getenv("PINATA_JWT")

def post_farcaster_reply(parent_hash, text):
    # We still use Pinata to SEND the reply (this part is usually still free)
    url = "https://api.pinata.cloud/v3/farcaster/casts"
    headers = {"Authorization": f"Bearer {PINATA_JWT}", "Content-Type": "application/json"}
    data = {"text": text, "parent": {"hash": parent_hash}}
    requests.post(url, json=data, headers=headers)

def judge_submission(image_url, bounty_name, skill):
    prompt = f"You are a professional {skill}. Judge this for '{bounty_name}'. If valid, say 'PASS' + compliment. If not, 'FAIL' + reason."
    img_data = requests.get(image_url).content
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, {"mime_type": "image/jpeg", "data": img_data}]
    )
    return response.text

def main():
    with open('active_bounties.json') as f:
        bounties = json.load(f)['bounties']

    for b in bounties:
        tag = b['id']
        print(f"Searching Neynar for #{tag}...")
        
        # Using Neynar's public search instead of Pinata
        url = f"https://api.neynar.com/v2/farcaster/cast/search?q={tag}"
        headers = {"api_key": NEYNAR_API_KEY}
        
        res = requests.get(url, headers=headers)
        casts = res.json().get('result', {}).get('casts', [])
        print(f"Found {len(casts)} posts.")

        for cast in casts:
            # Look for the image
            embeds = cast.get('embeds', [])
            image_url = next((e['url'] for e in embeds if 'url' in e and ('.jpg' in e['url'] or '.png' in e['url'])), None)
            
            if image_url:
                print(f"Judging post...")
                result = judge_submission(image_url, b['name'], b['skill'])
                post_farcaster_reply(cast['hash'], result)
                print("Success! Reply sent.")

if __name__ == "__main__":
    main()
