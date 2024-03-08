import os
from dotenv import load_dotenv

load_dotenv()

MASTODON_BASE_URL = 'https://vibecheck.masto.host'
MASTODON_CLIENT_ID = os.getenv('MASTODON_CLIENT_ID')
MASTODON_CLIENT_SECRET = os.getenv('MASTODON_CLIENT_SECRET')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
GMAIL_ACCOUNT = os.getenv('GMAIL_ACCOUNT')
ACCESS_TOKENS_FILE = 'access_tokens.json'


FEED_LIST = [
        {'url': 'https://feeds.feedblitz.com/marginalrevolution', 'username': 'mr_bot'},
        {'url': 'https://economistwritingeveryday.com/feed/', 'username': 'econ_writing_every_day'},
    ]

