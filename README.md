# VibeCheck 2.0

The goal of the project is to help users use AI to get the best internet
content. Stop using corporate algorithms and take back the power. Seek
immaculate vibes.

Initial prototype processes Mastodon content.

![Robot processing the internet to generate immaculate vibes for the benefit of all mankind, breathtaking surreal visualization, Hiroshi Nagai aesthetic](https://i.imgur.com/aruxdPe.png)

# Usage

Create a `.env` file containing `MASTODON_ACCESS_TOKEN`, `MASTODON_API_BASE_URL`  and `OPENAI_KEY`.

Create virtual environment with `poetry install`.

To pull toots and write them to a local DB:
`poetry run vibecheck/scrape_mastodon.py` 

To pull toots and write them to a local DB:
`poetry run vibecheck/create_algo_tags.py` to tag the toots.


