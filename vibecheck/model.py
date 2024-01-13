from datetime import datetime
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import re

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime objects to ISO format
        return json.JSONEncoder.default(self, obj)

# Define SQLite database and table using SQLAlchemy
Base = declarative_base()

class Toot(Base):
    __tablename__ = "toots"
    id = Column(Integer, primary_key=True)
    author = Column(String)
    content = Column(String)
    created_at = Column(DateTime)
    url = Column(String)
    raw_blob = Column(String)

    algo_tags = relationship("AlgoTags", backref="toots")

    @property
    def raw_dict(self):
        return json.loads(self.raw_blob)

    @property
    def display_name(self):
        return self.raw_dict["account"]["display_name"]

    @property
    def content_scrubbed(self):
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', self.content)
        return f'{self.display_name} posted: {text}'
    
    @staticmethod
    def dict_to_json(toot_dict):
        return json.dumps(toot_dict, cls=CustomJSONEncoder)

class AlgoTags(Base):
    __tablename__ = "algo_tags"
    id = Column(Integer, primary_key=True)
    tagger_version = Column(String)
    toot_id = Column(Integer, ForeignKey('toots.id'))
    tags_json = Column(String)

    @property
    def tags(self):
        return json.loads(self.tags_json)

    
def create_session():
    # Create SQLite database engine and session
    engine = create_engine("sqlite:///toots.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    return session
