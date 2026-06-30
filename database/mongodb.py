# ─────────────────────────────────────────────
#  database/mongodb.py
#  Handles the MongoDB connection for Sweet Bites
# ─────────────────────────────────────────────

from pymongo import MongoClient

def get_db():
    """
    Connect to MongoDB and return the database object.
    By default, connects to localhost on port 27017.
    Change the URI below if you use MongoDB Atlas or a different host.
    """
    client = MongoClient("mongodb://localhost:27017/")   # <-- change if needed
    db = client["sweet_bites_db"]                        # database name
    return db
