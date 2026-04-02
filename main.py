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
        # THE FIX: We use the ID but tell Pinata it's a hashtag in the URL
        tag_id = bounty['id'] 
        print(f"Searching Farcaster for mentions of #{tag_id}...")
        
        # We changed the URL slightly here to be more reliable
        search_url = f"https://api.pinata.cloud/v3/farcaster/casts?search=%23{tag_id}"
        headers = {"Authorization": f"Bearer {PINATA_JWT}"}
        
        response = requests.get(search_url, headers=headers)
        
        # Safety check: If Pinata fails, tell us why instead of crashing
        if response.status_code != 200:
            print(f"Pinata Error {response.status_code}: {response.text}")
            continue

        casts = response.json().get('casts', [])

        if not casts:
            print(f"No new posts found for #{tag_id}.")
            continue

        for cast in casts:
            embeds = cast.get('embeds', [])
            image_url = next((e['url'] for e in embeds if 'url' in e and ('.jpg' in e['url'] or '.png' in e['url'])), None)
            
            if image_url:
                print(f"Found image from {cast['author']['username']}. Judging...")
                result = judge_submission(image_url, bounty['name'], bounty['skill'])
                print(f"Result: {result}")
                post_farcaster_reply(cast['hash'], result)
                print("Reply posted successfully.")
