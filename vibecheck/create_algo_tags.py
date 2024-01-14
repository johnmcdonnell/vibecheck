from datetime import datetime, timedelta
from pydantic import BaseModel
from model import Toot, AlgoTags, create_session
from openai import OpenAI
import instructor
from loguru import logger

tagger_version = '0.1'

class TootTags(BaseModel):
    topic: str
    is_polemical: bool
    is_positive_valence: bool
    is_negative_valence: bool
    is_neutral_valence: bool
    is_emotional_language: bool
    is_political: bool
    is_academic: bool
    is_news: bool
    is_cringe: bool
    is_based: bool
    is_israel_palestine: bool
    is_joke: bool
    is_art: bool
    is_trolling: bool
    is_opinion: bool
    is_academic: bool
    is_informative: bool

def cleanup_toot_text(toot):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', toot.content)
    return f'{toot.display_name} posted: {text}'

def generate_algo_tags():
    session = create_session()
    instructor_client = instructor.patch(OpenAI())

    # Fetch toots from database that are less than two days old and missing from algo_tags table
    two_days_ago = datetime.now() - timedelta(days=2)
    toots = session.query(Toot).filter(Toot.created_at > two_days_ago).filter(~Toot.algo_tags.any()).all()

    toot_tags = []
    try:
        for toot in toots:
            logger.info('Tagging toot {}: {}'.format(toot.id, toot.content_scrubbed))
            toot_tagged = instructor_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    response_model=TootTags,
                    messages = [
                        {"role": "user", "content": f"Classify the following text: {toot.content_scrubbed}" }
                        ])

            new_algo_tags = AlgoTags(tagger_version=tagger_version, toot_id=toot.id, tags_json=toot_tagged.model_dump_json())
            session.add(new_algo_tags)

            logger.info('Tagged toot {} with tags {}'.format(toot.id, toot_tagged))
    finally:
        session.commit()

if __name__ == "__main__":
    generate_algo_tags()