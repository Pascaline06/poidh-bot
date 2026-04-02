import os
import json
import requests

# NOTE: Ensure NEYNAR_API_KEY is defined in your environment variables 
# or at the top of your script.
NEYNAR_API_KEY = os.getenv('NEYNAR_API_KEY')

def main():
    # 1. Check if the bounty file exists
    if not os.path.exists('active_bounties.json'):
        print("❌ Error: active_bounties.json not found in the root directory!")
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
        
        # We search for the tag string directly
        url = f"https://api.neynar.com/v2/farcaster/cast/search?q={tag}&priority_mode=false"
        headers = {"api_key": NEYNAR_API_KEY}
        
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status() 
            data = res.json()
            casts = data.get('result', {}).get('casts', [])
            
            if not casts:
                print(f"⌛ No results for {tag} yet. (Indexing can take 2-3 mins)")
                continue

            # This is the line you were looking for!
            print(f"✅ Found one! {tag} matches {len(casts)} potential posts.")

            for cast in casts:
                embeds = cast.get('embeds', [])
                image_url = next((e['url'] for e in embeds if 'url' in e and ('.jpg' in e['url'] or '.png' in e['url'])), None)
                
                if image_url:
                    print(f"⚖️ Judging post from @{cast['author']['username']}...")
                    
                    # Ensure judge_submission and post_farcaster_reply are defined/imported
                    result = judge_submission(image_url, b['name'], b['skill'])
                    print(f"📝 Result: {result}")
                    
                    post_farcaster_reply(cast['hash'], result)
                    print("✈️ Reply sent successfully!")
                else:
                    print(f"⏭️ Skipping cast {cast['hash']} - No image found.")

        except Exception as e:
            print(f"⚠️ Error during search for {tag}: {e}")

# --- THE FIX ---
# This block ensures the main() function actually runs when the file is called.
if __name__ == "__main__":
    main()
