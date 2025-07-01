from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv
from typing import TypedDict, List, Literal, Optional
from datetime import datetime

load_dotenv()

uri = os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client.get_database("Kakushin")

db.temp_sessions.create_index(
    [("createdAt", ASCENDING)],
    expireAfterSeconds=600
)

class User(TypedDict):
    name: str
    email: str
    google_access_token: Optional[str]
    google_refresh_token: Optional[str]
    type: Literal["volunteer", "organizer"]

class Event(TypedDict):
    name: str
    description: str
    location: str
    time: datetime
    users: List[User]
    guidelines: str
    resources: dict
    certificate_url: str
    attendance: List[User]
    feedback_form_url: str
    feed_back : dict

users = db["users"]
events = db["events"]