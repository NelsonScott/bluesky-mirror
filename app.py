import json
import os
from flask import Flask, redirect, request, render_template, session, url_for
from process_tweet import post_to_bluesky

app = Flask(__name__)
app.secret_key = os.environ.get('secret_key') or json.load(open("credentials.json"))['secret_key']

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        tweet_url = request.form.get('tweet_url')
        username = request.form.get('username')
        password = request.form.get('password')

        session['username'] = username
        session['password'] = password

        if tweet_url:
            try:
                post_to_bluesky(tweet_url, username, password)
                return redirect(url_for('home'))
            except Exception as e:
                return f"Error: {e}"
    
    username = session.get('username', '')
    password = session.get('password', '')

    return render_template('index.html', username=username, password=password)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
