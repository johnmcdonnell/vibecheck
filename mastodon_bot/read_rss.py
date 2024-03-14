import os
import json
import random
import requests
import string
import time

import anthropic
from bs4 import BeautifulSoup
import feedparser
from loguru import logger

from config import MASTODON_BASE_URL, MASTODON_CLIENT_ID, MASTODON_CLIENT_SECRET, CLAUDE_API_KEY, ACCESS_TOKENS_FILE, GMAIL_ACCOUNT, FEED_LIST




anthropic_client = anthropic.Anthropic(
    api_key=CLAUDE_API_KEY,
)


def parse_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    return feed.entries

def generate_summary(entry, max_retries=3):
    id = entry.get('id')
    author = entry.get('author')
    title = entry.get('title')
    if 'feedburner_origlink' in entry:
        link = entry.get('feedburner_origlink')
    else:
        link = entry.get('link')
    content = entry['content'][0]['value']
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    
    system_prompt = "Create a concise tweet that shares the thesis behind the blog post and why it might be interesting or surprising. Don't use hash tags. To the extent possible, match the tone of the author. Return ONLY the tweet, no other commentary."
    
    logger.info(f"Generating summary for post {id}")
    retries = 0
    delay = 2
    while retries < max_retries:
        try:
            message = anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=280,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Author: {author}\nTitle: {title}\nPost: {text}"
                            }
                        ]
                    }
                ]
            )
            return message.content[0].text, link
        except anthropic.RateLimitError:
            if retries < max_retries - 1:
                logger.warning(f"Anthropic rate limit exceeded, retrying in {delay} seconds")
                time.sleep(delay)
            else:
                raise "Max retries exceeded"

def create_mastodon_account(username, email, password):
    headers = {'Content-Type': 'application/json'}
    data = {
        'client_name': 'RSS Feed Bot',
        'redirect_uris': 'urn:ietf:wg:oauth:2.0:oob',
        'scopes': 'read write follow',
        'website': '',
    }
    response = requests.post(f'{MASTODON_BASE_URL}/api/v1/apps', headers=headers, json=data)
    client_id = response.json()['client_id']
    client_secret = response.json()['client_secret']

    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uris': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'client_credentials',
        'scope': 'read write follow',
    }
    token_response = requests.post(f'{MASTODON_BASE_URL}/oauth/token', data=token_data)
    if token_response.status_code == 200:
        access_token = token_response.json().get('access_token')
        logger.info(f'Access token obtained')
    else:
        logger.error(f'Failed to obtain access token. Status {response.status_code}: {response.json().get("error")}')
        access_token = None
        return None

    data = {
        'username': username,
        'email': email,
        'password': password,
        'agreement': True,
        'locale': 'en',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    logger.info(f'Creating account {username}')
    headers['Authorization'] = f'Bearer {access_token}'
    response = requests.post(f'{MASTODON_BASE_URL}/api/v1/accounts', headers=headers, json=data)
    logger.info(f'Mastodon returned status {response.status_code}: {response.json().get("error")}')
    access_token = response.json()['access_token']
    return access_token

def load_access_tokens():
    if os.path.exists(ACCESS_TOKENS_FILE):
        with open(ACCESS_TOKENS_FILE, 'r') as f:
            access_tokens = json.load(f)
    else:
        access_tokens = {}
    return access_tokens

def save_access_tokens(access_tokens):
    with open(ACCESS_TOKENS_FILE, 'w') as f:
        json.dump(access_tokens, f)

def post_to_mastodon(summary, url, access_token):
    logger.info(f"Posting text {summary}")
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'status': f'{summary}\n\n{url}'}
    response = requests.post(f'{MASTODON_BASE_URL}/api/v1/statuses', headers=headers, data=data)
    if 'error' in response.json():
        logger.info(f"Post to mastodon failed with status {response.status_code}: {response.json()}")
    else:
        logger.info(f"Posted to mastodon with status {response.status_code}")

def repost_rss(feeds):
    access_tokens = load_access_tokens()
    
    for feed in feeds:
        if feed['username'] not in access_tokens:
            feed_email = GMAIL_ACCOUNT + '+' + feed['username'] + '@gmail.com'
            feed_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            access_token = create_mastodon_account(feed['username'], feed_email, feed_password)
            access_tokens[feed['username']] = access_token
            save_access_tokens(access_tokens)
        else:
            access_token = access_tokens[feed['username']]
        
        entries = parse_rss_feed(feed['url'])
        logger.info(f"Parsing feed {feed['url']}")
        for entry in entries:
            summary, link = generate_summary(entry)
            post_to_mastodon(summary, link, access_token)
    

if __name__ == '__main__':
    repost_rss(FEED_LIST)
