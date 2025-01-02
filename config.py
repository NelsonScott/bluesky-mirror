import json

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def update_last_tweet_id(tweet_id: str):
    config = load_config()
    config['mirror']['last_mirrored_tweet_id'] = tweet_id
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
