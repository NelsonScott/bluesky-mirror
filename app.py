from flask import Flask, redirect, request, render_template, url_for
from process_tweet import post_to_bluesky

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        tweet_url = request.form.get('tweet_url')
        if tweet_url:
            try:
                post_to_bluesky(tweet_url)
                return redirect(url_for('home'))
            except Exception as e:
                return f"Error: {e}"
    return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000, debug=True)
