import json
import logging
from atproto import Client
from playwright.sync_api import sync_playwright
import requests

CREDS_PATH = "credentials.json"
HEADLESS = True

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_tweet_data(url: str) -> dict:
    """
    Scrape a single tweet page for Tweet data
    """
    logging.info(f"Starting to scrape tweet from URL: {url}")

    _xhr_calls = []

    def intercept_response(response):
        """capture all background requests and save them"""
        # we can extract details from background requests
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()


        # enable background request intercepting:
        page.on("response", intercept_response)
        # go to url and wait for the page to load
        page.goto(url)
        page.wait_for_selector("[data-testid='tweet']")

        # find all tweet background requests:
        tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
        for xhr in tweet_calls:
            data = xhr.json()
            logging.info("Successfully scraped tweet data.")
            return data['data']['tweetResult']['result']
    
    logging.warning("No tweet data found.")
    raise Exception("No tweet data found.")

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

def post_to_bluesky(tweet_url: str):
    """
    Post the scraped via Bluesky API
    """
    logging.info(f"Preparing to post to Bluesky for tweet URL: {tweet_url}")

    tweet_content = get_tweet_data(tweet_url)
    tweet_text = tweet_content['legacy']['full_text']
    logging.info(f"Tweet text scraped: {tweet_text}")
    tweet_text = _clean_tweet_text(tweet_text)
    logging.info(f"Tweet text cleaned: {tweet_text}")

    # Extract media URLs if available
    media_urls = []
    if 'extended_entities' in tweet_content['legacy']:
        media = tweet_content['legacy']['extended_entities']['media']
        for item in media:
            if item['type'] == 'video':
                variants = item['video_info']['variants']
                mp4_variants = [v for v in variants if v['content_type'] == 'video/mp4']
                if mp4_variants:
                    # Sort by bitrate and get the highest quality
                    highest_quality = max(mp4_variants, key=lambda x: x.get('bitrate', 0))
                    media_urls.append(highest_quality['url'])
            else:
                media_urls.append(item['media_url_https'])
        
        logging.info(f"Media URLs found: {media_urls}")

    client = Client()
    creds = json.load(open(CREDS_PATH))
    client.login(creds['username'], creds['password'])

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