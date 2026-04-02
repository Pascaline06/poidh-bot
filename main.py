def main():
    # Load your "Active Bounties" list
    if not os.path.exists('active_bounties.json'):
        print("Error: active_bounties.json not found!")
        return

    with open('active_bounties.json') as f:
        data = json.load(f)
        bounties = data['bounties']

    print(f"Bot Active! Monitoring {len(bounties)} bounties.")

    for b in bounties:
        tag = b['id']
        # THE FIX: We search for the tag WITHOUT the # symbol first. 
        # Neynar's 'q' parameter handles the search better as a plain string.
        print(f"Searching Neynar for {tag}...")
        
        url = f"https://api.neynar.com/v2/farcaster/cast/search?q={tag}&priority_mode=false"
        headers = {"api_key": NEYNAR_API_KEY}
        
        res = requests.get(url, headers=headers)
        
        # Log the raw result if we find nothing to help us debug
        data = res.json()
        casts = data.get('result', {}).get('casts', [])
        
        if not casts:
            print(f"No results for {tag}. Try waiting 2-3 minutes for indexing.")
            continue

        print(f"Found {len(casts)} potential posts!")

        for cast in casts:
            # Check for images
            embeds = cast.get('embeds', [])
            image_url = next((e['url'] for e in embeds if 'url' in e and ('.jpg' in e['url'] or '.png' in e['url'])), None)
            
            if image_url:
                print(f"Judging post from {cast['author']['username']}...")
                result = judge_submission(image_url, b['name'], b['skill'])
                print(f"Result: {result}")
                post_farcaster_reply(cast['hash'], result)
                print("Reply sent successfully!")
