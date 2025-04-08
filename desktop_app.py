import webview
import threading
import time
from run import create_db_and_tables, app, mirror_tweets

# TODO: this was all auto genrated(mostly) and I think repeats a lot of code
# make sure clean this up before committing

# API class to expose Python functions to JavaScript
class BlueskyMirrorAPI:
    def mirror_tweet(self, url, username, password):
        """Mirror a single tweet to Bluesky"""
        try:
            from twitter_client import get_single_tweet_data
            from bluesky_client import post_to_bluesky
            
            tweet = get_single_tweet_data(url)
            post_to_bluesky(tweet, username, password)
            return {"success": True, "message": "Tweet mirrored successfully!"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_config(self):
        """Get the configuration"""
        try:
            from config import load_config
            config = load_config()
            return {
                "bluesky_username": config["bluesky"]["username"],
                # Omit password for security
            }
        except Exception as e:
            return {"error": str(e)}

# Start the Flask server in a separate thread
DESKTOP_PORT = 5005
def start_flask():
    # Use host 127.0.0.1 instead of 0.0.0.0 for security in desktop app
    app.run(host="127.0.0.1", port=DESKTOP_PORT, debug=False)

def main():
    # Create database tables
    create_db_and_tables()
    
    # Start Flask server in a thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask a moment to start up
    time.sleep(1)
    
    # Start background mirroring service
    mirror_thread = threading.Thread(target=mirror_tweets, daemon=True)
    mirror_thread.start()
    
    # Create window with our API
    api = BlueskyMirrorAPI()
    window = webview.create_window(
        title='Bluesky Mirror', 
        url=f'http://127.0.0.1:{DESKTOP_PORT}',
        js_api=api,
        width=1000,
        height=700,
        resizable=True,
        min_size=(800, 600)
    )
    
    # Start the PyWebView app
    webview.start(debug=True)

if __name__ == "__main__":
    main()