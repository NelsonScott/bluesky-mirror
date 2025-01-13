from playwright.sync_api import sync_playwright

def save_twitter_auth_state():
    with sync_playwright() as p:
        # Launch browser in headed mode
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Open Twitter
        page = context.new_page()
        page.goto('https://twitter.com')
        
        input("Log in manually in the browser window, then press Enter here to save the state...")
        
        # Save the authentication state
        context.storage_state(path="twitter_auth.json")
        print("Auth state saved to twitter_auth.json")
        browser.close()

if __name__ == "__main__":
    save_twitter_auth_state()