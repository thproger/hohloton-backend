from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.core.config import MONGODB_DB_NAME, MONGODB_URL

mongo_client: MongoClient[Any] = MongoClient(MONGODB_URL)
db: Database[Any] = mongo_client[MONGODB_DB_NAME]
users_collection: Collection[Any] = db["users"]
businesses_collection: Collection[Any] = db["businesses"]
