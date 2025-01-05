import colorlog
import requests
from atproto import Client

from tweet import Tweet

logger = colorlog.getLogger(__name__)


def post_to_bluesky(tweet: Tweet, username: str, password: str):
    """
    Post the scraped via bluesky api
    """
    tweet_text = tweet.text
    logger.info(f"Tweet text scraped: {tweet_text}")
    tweet_text = _clean_tweet_text(tweet_text)
    logger.info(f"Tweet text cleaned: {tweet_text}")

    # extract media urls if available
    media_urls = tweet.media_urls
    logger.info(f"Media urls found: {media_urls}")

    client = Client()
    client.login(username, password)

    if not media_urls:
        logger.info("No media urls found.")
        logger.info(f"Posting tweet without image.")
        return client.send_post(tweet_text)

    images_data = []
    for url in media_urls:
        try:
            # check if it's a video url (looking for typical video path indicators)
            is_video = any(x in url.lower() for x in ["/video/", ".mp4", "vid/"])

            response = requests.get(url)
            response.raise_for_status()  # raise exception for bad status codes
            if is_video:
                logger.info(f"uploading video from {url}")
                return client.send_video(text=tweet_text, video=response.content, video_alt="video")
            else:
                logger.info(f"downloading image from {url}")
                images_data.append(response.content)
        except Exception as e:
            logger.error(f"error processing media url {url}: {str(e)}")
            continue

    if images_data:
        logger.info(f"posting with {len(images_data)} images")
        image_alts = [f"image {i}" for i in range(len(images_data))]
        return client.send_images(text=tweet_text, images=images_data, image_alts=image_alts)
    else:
        logger.warning("failed to process any media. posting text only.")
        return client.send_post(tweet_text)


def _clean_tweet_text(full_text: str) -> str:
    """
    Clean tweet text by removing t.co URLs

    Args:
        full_text (str): Raw tweet text from Twitter API

    Returns:
        str: Cleaned tweet text without t.co URLs
    """
    # Regular expression to match t.co URLs
    import re

    # Remove t.co URLs
    cleaned_text = re.sub(r"https://t\.co/\w+", "", full_text).strip()

    return cleaned_text
