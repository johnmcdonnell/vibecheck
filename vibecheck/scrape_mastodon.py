import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
from mastodon import Mastodon
from urllib.parse import urlparse
from loguru import logger

from model import Toot, create_session

load_dotenv()

# Get Mastodon credentials from environment variables
#client_id = os.getenv("MASTODON_CLIENT_ID")
#client_secret = os.getenv("MASTODON_CLIENT_SECRET")
access_token = os.getenv("MASTODON_ACCESS_TOKEN")
api_base_url = os.getenv("MASTODON_API_BASE_URL")
print('API base URL:')
print(api_base_url)

mastodon = Mastodon(
    access_token=access_token,
    api_base_url=api_base_url
)

# Use the Mastodon API to fetch the toots from the last two days with requests

if __name__ == "__main__":
    session = create_session()

    # Get the datetime for two days ago
    two_days_ago = datetime.now() - timedelta(days=2)

    # Scrape the feed for toots from the last two days
    toots = mastodon.timeline(timeline="public", since_id=two_days_ago)

    # Store the toots in the SQLite database
    for toot in toots:
        # Convert toot to json
        toot_json = Toot.dict_to_json(dict(toot))

        new_toot = Toot(id=toot["id"], author=toot["account"]["acct"], content=toot["content"], created_at=toot["created_at"], url=toot["url"], raw_blob=toot_json)
        session.add(new_toot)

    session.commit()
    logger.info('Scraped {} toots from Mastodon'.format(len(toots)))
