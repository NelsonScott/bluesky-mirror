import time
from typing import List
from app import app
from threading import Thread
from bluesky_client import post_to_bluesky
from tweet import Tweet
from twitter_client import get_user_tweets_data

from config import load_config, update_last_tweet_id

MIRROR_INTERVAL = 8

def mirror_tweets():
    while True:
        try:
            config = load_config()
            blue_sky_config = config["bluesky"]
            mirror_config = config["mirror"]

            print("we need proper logging; anyway starting to mirror tweets")
            # TODO: max tweets limit seems to be ignored
            tweets: List[Tweet] = get_user_tweets_data(username=mirror_config["twitter_account"], max_tweets=1)
            if mirror_config["last_mirrored_tweet_id"] is None or mirror_config["last_mirrored_tweet_id"] != tweets[0].id:
                post_to_bluesky(tweet=tweets[0], username=blue_sky_config['username'], password=blue_sky_config['password'])
                update_last_tweet_id(tweets[0].id)
            else:
                print("No new tweets to mirror")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            time.sleep(MIRROR_INTERVAL)

if __name__ == "__main__":
    thread = Thread(target=mirror_tweets, daemon=True)
    thread.start()

    # Start the Flask app (with reloader disabled to prevent duplicate threads)
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)