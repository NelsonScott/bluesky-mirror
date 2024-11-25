# 🐦 Bluesky Mirror 🦋
A simple tool to copy a Tweet and post it directly to Bluesky with a friendly interface.

Just run the app, enter a twitter URL and it'll scrape the data for you and post it on Bluesky.

## Features
📤 **Tweet to Bluesky Posting**: Quickly repost any Tweet to Bluesky by providing its URL.  
**Save Your Favorites**: Since there's no bookmarks, save your favorites in one account.

## Setup
Clone the repository:
```bash
git clone git@github.com:NelsonScott/bluesky-mirror.git
cd bluesky-mirror
pipenv install

# set a 'secret_key' in credentials.json, then you can run it locally
make dev-run
```

## License
This project is licensed under the MIT License.

## Acknowledgements
* Reliable strategy scrape found @ https://scrapfly.io/blog/how-to-scrape-twitter/
* Helpful examples for BSky API @ https://github.com/MarshalX/atproto/tree/main/examples
* Built with 💻 and ☕.

## TODO
* Frontend to display results and error states dynamically.
* Add screenshot preview in readme
* Add demo on either Render or Railway
* update tags twitter content to bluesky username