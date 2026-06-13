"""
Seed MongoDB Atlas with demo data.
Run: python -m db.seed
"""
from db.mock_db import (
    USERS, ORDERS, REFURBISHED_PRODUCTS, LIFECYCLE_EVENTS,
    NOTIFICATIONS, RETURN_SIGNALS, CART_EVENTS
)
from config import settings

if not settings.MONGO_URI:
    print("❌ MONGO_URI not set. Add it to .env first.")
    exit(1)

from pymongo import MongoClient

client = MongoClient(settings.MONGO_URI)
database = client.get_database("relife_ai")


def seed():
    print("🌱 Seeding MongoDB Atlas...")

    # Users
    database.users.delete_many({})
    database.users.insert_many(list(USERS.values()))
    print(f"   ✅ Users: {len(USERS)}")

    # Orders
    database.orders.delete_many({})
    database.orders.insert_many(ORDERS)
    print(f"   ✅ Orders: {len(ORDERS)}")

    # Refurbished Products
    database.refurbished_products.delete_many({})
    database.refurbished_products.insert_many(REFURBISHED_PRODUCTS)
    print(f"   ✅ Refurbished Products: {len(REFURBISHED_PRODUCTS)}")

    # Lifecycle Events
    database.lifecycle_events.delete_many({})
    database.lifecycle_events.insert_many(LIFECYCLE_EVENTS)
    print(f"   ✅ Lifecycle Events: {len(LIFECYCLE_EVENTS)}")

    # Notifications
    database.notifications.delete_many({})
    database.notifications.insert_many(NOTIFICATIONS)
    print(f"   ✅ Notifications: {len(NOTIFICATIONS)}")

    # Return Signals
    database.return_signals.delete_many({})
    database.return_signals.insert_many(list(RETURN_SIGNALS.values()))
    print(f"   ✅ Return Signals: {len(RETURN_SIGNALS)}")

    # Cart Events
    database.cart_events.delete_many({})
    database.cart_events.insert_many(CART_EVENTS)
    print(f"   ✅ Cart Events: {len(CART_EVENTS)}")

    print("\n🎉 Database seeded successfully!")
    print(f"   Database: relife_ai")
    print(f"   URI: {settings.MONGO_URI[:40]}...")


if __name__ == "__main__":
    seed()
