# ─────────────────────────────────────────────
#  database/mongodb.py
#  Handles the MongoDB connection for Sweet Bites
# ─────────────────────────────────────────────

from pymongo import MongoClient
import os

def get_db():
    """
    Connect to MongoDB and return the database object.
    By default, connects to localhost on port 27017.
    Change the URI below if you use MongoDB Atlas or a different host.
    """
    MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
    )

    client = MongoClient(MONGO_URI)
    #client = MongoClient("mongodb://localhost:27017/")   # <-- change if needed
    db = client["sweet_bites_db"]                        # database name
    return db
