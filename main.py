import os
import json
import requests
from google import genai

# 1. Setup
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
PINATA_JWT = os.getenv("PINATA_JWT")

def post_farcaster_reply(parent_hash, text):
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

    print(f"Bot Active! Monitoring {len(bounties)} bounties.")

    for b in bounties:
        tag = b['id']
        print(f"Searching Farcaster for #{tag}...")
        
        # PINATA V3 UPDATE: This is the specific URL for searching text/hashtags
        url = f"https://api.pinata.cloud/v3/farcaster/casts/search?text={tag}"
        headers = {"Authorization": f"Bearer {PINATA_JWT}"}
        
        res = requests.get(url, headers=headers)
        
        if res.status_code != 200:
            print(f"Pinata Error {res.status_code}: {res.text}")
            continue

        # V3 search returns results inside 'data' -> 'casts'
        data = res.json().get('data', {})
        casts = data.get('casts', [])
        print(f"Found {len(casts)} potential posts.")

        for cast in casts:
            embeds = cast.get('embeds', [])
            image_url = next((e['url'] for e in embeds if 'url' in e and ('.jpg' in e['url'] or '.png' in e['url'])), None)
            
            if image_url:
                print(f"Judging post from {cast['author']['username']}...")
                result = judge_submission(image_url, b['name'], b['skill'])
                print(f"Result: {result}")
                post_farcaster_reply(cast['hash'], result)
                print("Reply sent!")

if __name__ == "__main__":
    main()
