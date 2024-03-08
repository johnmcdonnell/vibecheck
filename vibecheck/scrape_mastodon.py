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
access_token = os.getenv("MASTODON_ACCESS_TOKEN")
api_base_url = os.getenv("MASTODON_API_BASE_URL")

mastodon = Mastodon(access_token=access_token, api_base_url=api_base_url)


# Use the Mastodon API to fetch the toots from the last two days with requests

if __name__ == "__main__":
    session = create_session()

    # Scrape the feed for toots from the last two days
    toots = mastodon.timeline(timeline="public", limit=40)
    #toots = mastodon.account_statuses('895746', limit=40)

    # Store the toots in the SQLite database
    for toot in toots:
        # Convert toot to json
        toot_json = Toot.dict_to_json(dict(toot))
        if 'reblog' in toot and toot['reblog'] is not None:
            toot_author = toot['reblog']['account']['acct']
            toot_content = toot['reblog']['content']
        else:
            toot_author = toot['account']['acct']
            toot_content = toot['content']
        new_toot = Toot(
            id=toot["id"],
            author=toot_author,
            content=toot_content,
            created_at=toot["created_at"],
            url=toot["url"],
            raw_blob=toot_json,
        )
        session.add(new_toot)

    session.commit()
    logger.info("Scraped {} toots from Mastodon".format(len(toots)))
