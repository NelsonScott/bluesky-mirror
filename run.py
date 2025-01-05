import time
import logging
from typing import List
from threading import Thread

import colorlog

from app import app
from bluesky_client import post_to_bluesky
from tweet import Tweet
from twitter_client import get_user_tweets_data
from config import load_config, update_last_tweet_id

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s%(reset)s",
        datefmt="%m/%d %I:%M:%S %p",  # Gives you: 01/02 04:37:34 PM
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
)

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


MIRROR_INTERVAL = 60 * 60  # 3600 seconds (1 hours)


def mirror_tweets():
    """
    Main loop that checks for new tweets and mirrors them to Bluesky.
    Runs continuously with error handling and retry logic.
    """
    while True:
        try:
            config = load_config()
            bluesky_config = config["bluesky"]
            mirror_config = config["mirror"]

            logging.info("Checking for new tweets from @%s", mirror_config["twitter_account"])

            # TODO: max tweet limit seems ignored
            tweets: List[Tweet] = get_user_tweets_data(username=mirror_config["twitter_account"], max_tweets=1)

            if not tweets:
                logging.info("No tweets found")
                continue

            latest_tweet = tweets[0]
            last_mirrored_id = mirror_config["last_mirrored_tweet_id"]

            # Check if we have a new tweet to mirror
            if last_mirrored_id is None or last_mirrored_id != latest_tweet.id:
                logging.info("Found new tweet (ID: %s), mirroring to Bluesky", latest_tweet.id)
                post_to_bluesky(
                    tweet=latest_tweet,
                    username=bluesky_config["username"],
                    password=bluesky_config["password"],
                )
                update_last_tweet_id(latest_tweet.id)
                logging.info("Successfully mirrored tweet")
            else:
                logging.info("No new tweets to mirror")

        except Exception as e:
            logging.error("Error during mirroring: %s", str(e))
        finally:
            time.sleep(MIRROR_INTERVAL)


if __name__ == "__main__":
    logging.info("Starting tweet mirror service")
    thread = Thread(target=mirror_tweets, daemon=True)
    thread.start()

    logging.info("Starting web application")
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
        use_reloader=False,  # Prevent duplicate threads in debug mode
    )
