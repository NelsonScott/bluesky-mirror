import json
import colorlog
import time
from typing import List 
from playwright.sync_api import sync_playwright

from tweet import Tweet

logger = colorlog.getLogger(__name__)

HEADLESS = True
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def get_single_tweet_data(url: str) -> Tweet:
    """
    Scrape a single tweet page for Tweet data

    Args:
        url: URL of the tweet to scrape

    Returns:
        Tweet: Tweet dataclass object containing the tweet data

    Raises:
        Exception: If no tweet data is found
    """
    logger.info(f"Starting to scrape tweet from URL: {url}")
    xhr_calls = []

    def handle_response(response):
        if response.request.resource_type == "xhr":
            xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=HEADLESS)
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()
            page.on("response", handle_response)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_selector("[data-testid='tweet']")

            tweet_calls = [f for f in xhr_calls if "TweetResultByRestId" in f.url]
            for xhr in tweet_calls:
                data = xhr.json()
                tweet_data = data["data"]["tweetResult"]["result"]
                logger.info("Successfully scraped tweet data.")
                return Tweet.from_api_response(tweet_data)

            logger.warning("No tweet data found.")
            raise Exception("No tweet data found.")
        finally:
            if "browser" in locals():
                browser.close()


def get_user_tweets_data(username: str, max_tweets: int = 10) -> List[Tweet]:
    """
    Scrape recent tweets from a user's profile

    Args:
        username (str): Twitter username without '@'
        max_tweets (int): Maximum number of tweets to scrape

    Returns:
        List List of Tweet objects scraped from the user's profile
    """
    logger.info(f"Starting to scrape tweets from user: {username}")
    tweets_data = []
    xhr_calls = []

    def handle_response(response):
        try:
            if "UserTweets" in response.url and response.status == 200:
                xhr_calls.append(response)
                try:
                    data = response.json()
                    if "data" in data:
                        timeline_entries = (
                            data.get("data", {})
                            .get("user", {})
                            .get("result", {})
                            .get("timeline_v2", {})
                            .get("timeline", {})
                            .get("instructions", [])
                        )

                        for instruction in timeline_entries:
                            if instruction.get("type") == "TimelineAddEntries":
                                for entry in instruction.get("entries", []):
                                    result = (
                                        entry.get("content", {})
                                        .get("itemContent", {})
                                        .get("tweet_results", {})
                                        .get("result", {})
                                    )

                                    if result and result not in tweets_data:
                                        # temporary debug
                                        with open(f'tweet_response_{len(tweets_data)}.json', 'w') as f:
                                            json.dump(result, f, indent=2)
                                        tweets_data.append(result)
                                        logger.info(f"Found tweet: {len(tweets_data)}")

                except Exception as e:
                    logger.error(f"Error processing response JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error in response handler: {str(e)}")

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=HEADLESS)
            context = browser.new_context(
                storage_state="twitter_auth.json",
                user_agent=USER_AGENT,
                viewport={"width": 1920, "height": 1080},
            )

            page = context.new_page()
            page.on("response", handle_response)

            profile_url = f"https://twitter.com/{username}"
            logger.info(f"Navigating to: {profile_url}")
            page.goto(profile_url)

            page.wait_for_selector("article[data-testid='tweet']", timeout=10000)
            time.sleep(2)  # Initial pause for dynamic content

            scroll_attempts = 0
            max_scroll_attempts = 5

            while len(tweets_data) < max_tweets and scroll_attempts < max_scroll_attempts:
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(2)
                scroll_attempts += 1
                logger.info(f"Scroll attempt {scroll_attempts}, found {len(tweets_data)} tweets")

            if len(tweets_data) == 0:
                logger.warning("No tweets found. Debug info:")
                logger.warning(f"Number of XHR calls captured: {len(xhr_calls)}")
                for i, call in enumerate(xhr_calls):
                    try:
                        data = call.json()
                        logger.warning(f"XHR call {i + 1} data structure:")
                        logger.warning(json.dumps(data, indent=2)[:500] + "...")
                    except Exception as e:
                        logger.error(f"Error parsing XHR call {i + 1}: {str(e)}")

            tweets = [Tweet.from_api_response(tweet_data) for tweet_data in tweets_data]
            non_retweet_tweets = [tweet for tweet in tweets if not tweet.is_retweet]
            
            if len(tweets) != len(non_retweet_tweets):
                logger.info(f"Filtered out {len(tweets) - len(non_retweet_tweets)} retweets")

            return non_retweet_tweets

        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return []
        finally:
            if "browser" in locals():
                browser.close()
