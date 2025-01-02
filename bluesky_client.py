import logging
import requests
from atproto import Client

from tweet import Tweet

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def post_to_bluesky(tweet: Tweet, username: str, password: str):
    """
    Post the scraped via Bluesky API
    """
    tweet_text = tweet.text
    logging.info(f"Tweet text scraped: {tweet_text}")
    tweet_text = _clean_tweet_text(tweet_text)
    logging.info(f"Tweet text cleaned: {tweet_text}")

    # Extract media URLs if available
    media_urls = tweet.media_urls        
    logging.info(f"Media URLs found: {media_urls}")

    client = Client()
    client.login(username, password)

    if not media_urls:
        logging.info("No media URLs found.")
        logging.info(f"Posting tweet without image.")
        return client.send_post(tweet_text)
    
    images_data = []
    for url in media_urls:
        try:
            # Check if it's a video URL (looking for typical video path indicators)
            is_video = any(x in url.lower() for x in ['/video/', '.mp4', 'vid/'])
            
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for bad status codes
            if is_video:
                logging.info(f"Uploading video from {url}")
                return client.send_video(text=tweet_text, video=response.content, video_alt='video')
            else:
                logging.info(f"Downloading image from {url}")
                images_data.append(response.content)
        except Exception as e:
            logging.error(f"Error processing media URL {url}: {str(e)}")
            continue

    if images_data:
        logging.info(f"Posting with {len(images_data)} images")
        image_alts = [f"Image {i}" for i in range(len(images_data))]
        return client.send_images(text=tweet_text, images=images_data, image_alts=image_alts)
    else:
        logging.warning("Failed to process any media. Posting text only.")
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
    cleaned_text = re.sub(r'https://t\.co/\w+', '', full_text).strip()
    
    return cleaned_text
