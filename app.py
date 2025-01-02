import json
import os
from flask import Flask, redirect, request, render_template, session, url_for
from bluesky_client import post_to_bluesky
from twitter_client import get_single_tweet_data

from config import load_config

app = Flask(__name__)
app.secret_key = load_config()['secret_key']

# routes
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
                tweet_content = get_single_tweet_data(tweet_url)
                post_to_bluesky(tweet_content=tweet_content, username=username, password=password)
                return redirect(url_for('home'))
            except Exception as e:
                return f"Error: {e}"
    
    username = session.get('username', '')
    password = session.get('password', '')

    return render_template('index.html', username=username, password=password)