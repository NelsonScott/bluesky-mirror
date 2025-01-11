from datetime import datetime, timezone
import time
import logging
from typing import List
from threading import Thread

import colorlog
from sqlmodel import Session

from app import app
from bluesky_client import post_to_bluesky
from database import create_db_and_tables, engine
from tweet import Tweet
from twitter_client import get_user_tweets_data
from config import load_config

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s%(reset)s",
        datefmt="%m/%d %I:%M:%S %p %Z",  # exp "01/02 04:37:34 PM EST"
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
    """
    while True:
        try:
            config = load_config()
            accounts_to_mirror = config["accounts_to_mirror"]

            for account_config in accounts_to_mirror:
                logging.info("Checking for new tweets from @%s", account_config["twitter_account"])

                # TODO: max tweet limit seems ignored
                tweets: List[Tweet] = get_user_tweets_data(username=account_config["twitter_account"], max_tweets=1)

                if not tweets:
                    logging.info("No tweets found")
                    continue

                latest_tweet = tweets[0]
                mirror_tweet(latest_tweet, config)
        except Exception as e:
            logging.error("Critical error in tweet mirroring process", exc_info=True)
        finally:
            time.sleep(MIRROR_INTERVAL)

def mirror_tweet(tweet: Tweet, config: dict):
    """
    Mirror a single tweet to Bluesky.
    """
    logging.info("Mirroring tweet: %s", tweet.text)
    bluesky_config = config["bluesky"]

    with Session(engine) as session:
        tweet_in_db = session.get(Tweet, tweet.id)
        if tweet_in_db and tweet_in_db.mirrored_at:
            logging.info("Tweet already mirrored")
        else:
            logging.info("Found new tweet (ID: %s), mirroring to Bluesky", tweet.id)
            post_to_bluesky(
                tweet=tweet,
                username=bluesky_config["username"],
                password=bluesky_config["password"],
            )

            if not tweet_in_db:
                tweet_in_db = tweet
                session.add(tweet_in_db)
            tweet_in_db.mirrored_at = datetime.now(timezone.utc)
            session.commit()
            logging.info("Successfully mirrored tweet")

if __name__ == "__main__":
    logging.info("Starting tweet mirror service")
    create_db_and_tables()

    thread = Thread(target=mirror_tweets, daemon=True)
    thread.start()

    logging.info("Starting web application")
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
        use_reloader=False,  # Prevent duplicate threads in debug mode
    )
