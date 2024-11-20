import json
from atproto import Client
from playwright.sync_api import sync_playwright
import requests

CREDS_PATH = "credentials.json"
HEADLESS = False

def get_tweet_data(url: str) -> dict:
    """
    Scrape a single tweet page for Tweet data
    """
    _xhr_calls = []

    def intercept_response(response):
        """capture all background requests and save them"""
        # we can extract details from background requests
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
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
            return data['data']['tweetResult']['result']

def post_to_bluesky(tweet_url: str):
    """
    Post the scraped via Bluesky API
    """
    tweet_content = get_tweet_data(tweet_url)
    tweet_text = tweet_content['legacy']['full_text']

    # Extract media URLs if available
    media_urls = []
    if 'extended_entities' in tweet_content['legacy']:
        media = tweet_content['legacy']['extended_entities']['media']
        media_urls = [item['media_url_https'] for item in media]

    client = Client()
    creds = json.load(open(CREDS_PATH))
    username = creds['username']
    password = creds['password']
    client.login(username, password)
    
    # Download media files
    if media_urls:
        print(f"\n\nMedia URLs: {media_urls}")
        img_data = requests.get(media_urls[0]).content
        post = client.send_image(text=tweet_text, image=img_data, image_alt="Image Alt")
    else:
        post = client.send_post(tweet_text)

    return post