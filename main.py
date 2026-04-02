import os
import json
import requests
from google import genai

# 1. Setup Connections
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
PINATA_JWT = os.getenv("PINATA_JWT")

def post_farcaster_reply(parent_hash, text):
    """The Voice: Posts a reply to Farcaster via Pinata"""
    url = "https://api.pinata.cloud/v3/farcaster/casts"
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "parent": {"hash": parent_hash}
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def judge_submission(image_url, bounty_name, skill):
    """The Brain: Uses Gemini to judge the image"""
    prompt = (
        f"You are a professional {skill}. "
        f"Judge this image for the '{bounty_name}' bounty. "
        "If it is valid, reply with 'PASS' and a 1-sentence compliment. "
        "If it is invalid, reply with 'FAIL' and a polite reason why."
    )
    
    # Download the image from Farcaster to show Gemini
    img_data = requests.get(image_url).content
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, {"mime_type": "image/jpeg", "data": img_data}]
    )
    return response.text

def main():
    # Load your "Active Bounties" list
    if not os.path.exists('active_bounties.json'):
        print("Error: active_bounties.json not found!")
        return

    with open('active_bounties.json') as f:
        data = json.load(f)
        bounties = data['bounties']

    print(f"Bot Active! Monitoring {len(bounties)} bounties.")

    for bounty in bounties:
        # THE FIX: This adds the # so it finds your hashtag correctly
        tag = f"#{bounty['id']}" 
        print(f"Searching Farcaster for mentions of {tag}...")
        
        search_url = f"https://api.pinata.cloud/v3/farcaster/casts?search={tag}"
        headers = {"Authorization": f"Bearer {PINATA_JWT}"}
        
        response = requests.get(search_url, headers=headers)
        casts = response.json().get('casts', [])

        if not casts:
            print(f"No new posts found for {tag}.")
            continue

        for cast in casts:
            # Check for images in the post
            embeds = cast.get('embeds', [])
            image_url = next((e['url'] for e in embeds if 'url' in e and ('.jpg' in e['url'] or '.png' in e['url'])), None)
            
            if image_url:
                print(f"Found image from {cast['author']['username']}. Judging...")
                result = judge_submission(image_url, bounty['name'], bounty['skill'])
                
                print(f"Result: {result}")
                
                # Post the reply!
                post_farcaster_reply(cast['hash'], result)
                print("Reply posted successfully.")

if __name__ == "__main__":
    main()
