"""
ReLife AI — Real MongoDB Atlas connection.
Used when MONGO_URI is set in environment.
"""
from pymongo import MongoClient
from config import settings

# Connect to MongoDB Atlas (Free M0 cluster)
client = MongoClient(settings.MONGO_URI)
_database = client.get_database("relife_ai")


class _DB:
    """Exposes collections matching the mock_db interface."""
    users = _database["users"]
    orders = _database["orders"]
    refurbished_products = _database["refurbished_products"]
    lifecycle_events = _database["lifecycle_events"]
    p2p_requests = _database["p2p_requests"]
    p2p_listings = _database["p2p_listings"]
    notifications = _database["notifications"]
    return_signals = _database["return_signals"]
    cart_events = _database["cart_events"]
    product_ratings = _database["product_ratings"]
    p2p_chats = _database["p2p_chats"]


db = _DB()
