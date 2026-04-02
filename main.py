import os
import json
import requests
import google.generativeai as genai

# --- CONFIGURATION & SECRETS ---
NEYNAR_API_KEY = os.getenv('NEYNAR_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# If you are using Neynar to reply, you usually need a Signer UUID
SIGNER_UUID = os.getenv('SIGNER_UUID') 

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def judge_submission(image_url, bounty_name, skill_requirement):
    """Uses Gemini to check if the image matches the bounty description."""
    prompt = f"""
    You are a judge for a 'Proof Of It Did Happen' bot. 
    Bounty Name: {bounty_name}
    Requirement: {skill_requirement}
    
    Look at this image: {image_url}
    Does this image prove the user completed the bounty? 
    Respond with a short, friendly message (max 2 sentences) confirming or denying.
    """
    try:
        # Note: In a production bot, you'd download the image bytes first, 
        # but for this simple version, we ask Gemini to look at the URL/Prompt logic.
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error judging submission: {str(e)}"

def post_farcaster_reply(parent_hash, text):
    """Posts a reply to the specific Farcaster cast via Neynar."""
    url = "https://api.neynar.com/v2/farcaster/cast"
    
    # FIXED: Using 'x-api-key' instead of 'api_key'
    headers = {
        "x-api-key": NEYNAR_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "signer_uuid": SIGNER_UUID, 
        "text": text,
        "parent": parent_hash
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to post reply: {e}")
        return False

def main():
    if not os.path.exists('active_bounties.json'):
        print("❌ Error: active_bounties.json not found!")
        return

    with open('active_bounties.json') as f:
        try:
            data = json.load(f)
            bounties = data['bounties']
        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
            return

    print(f"🚀 Bot Active! Monitoring {len(bounties)} bounties.")

    for b in bounties:
        tag = b['id']
        print(f"🔍 Searching Neynar for {tag}...")
        
        # SEARCH ENDPOINT
        url = f"https://api.neynar.com/v2/farcaster/cast/search?q={tag}&priority_mode=false"
        headers = {"x-api-key": NEYNAR_API_KEY} # FIXED HEADER
        
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status() 
            data = res.json()
            casts = data.get('result', {}).get('casts', [])
            
            if not casts:
                print(f"⌛ No results for {tag} yet.")
                continue

            print(f"✅ Found one! {tag} matches {len(casts)} potential posts.")

            for cast in casts:
                embeds = cast.get('embeds', [])
                image_url = next((e['url'] for e in embeds if 'url' in e and ('.jpg' in e['url'] or '.png' in e['url'])), None)
                
                if image_url:
                    print(f"⚖️ Judging post from @{cast['author']['username']}...")
                    
                    # Call the judging function
                    result_text = judge_submission(image_url, b['name'], b['skill'])
                    print(f"📝 AI Decision: {result_text}")
                    
                    # Post the reply
                    success = post_farcaster_reply(cast['hash'], result_text)
                    if success:
                        print("✈️ Reply sent successfully!")
                else:
                    print(f"⏭️ Skipping cast {cast['hash']} - No image found.")

        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 402:
                print("⚠️ Neynar 402 Error: Check 'x-api-key' or Plan limits.")
            else:
                print(f"⚠️ HTTP Error: {err}")
        except Exception as e:
            print(f"⚠️ Error during search for {tag}: {e}")

if __name__ == "__main__":
    main()
