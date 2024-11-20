import json
from atproto import Client
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

CREDS_PATH = "credentials.json"

def get_tweet_text(tweet_url):
    # Send a GET request to the tweet URL
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(tweet_url, headers=headers)
    
    if response.status_code != 200:
        return f"Failed to fetch the tweet. Status code: {response.status_code}"
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the tweet text (adjust the selector if needed)
    try:
        tweet_text = soup.find('div', {'data-testid': 'tweetText'}).text.strip()
        return tweet_text
    except AttributeError:
        return "Could not find tweet text. The structure might have changed."

def scrape_tweet(url: str) -> dict:
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
        browser = pw.chromium.launch(headless=False)
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

def post_to_bluesky(tweet_body: str):
    """
    Post the scraped via Bluesky API
    """

    client = Client()
    creds = json.load(open(CREDS_PATH))
    username = creds['username']
    password = creds['password']
    client.login(username, password)
    
    post = client.send_post(tweet_body)


if __name__ == "__main__":
    #TODO: accept tweet input
    tweet_url = ""
    worst_grades_tweet = scrape_tweet(tweet_url)
    full_text = worst_grades_tweet['legacy']['full_text']
    post_to_bluesky(full_text)