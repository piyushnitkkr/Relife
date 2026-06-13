"""
ReLife AI — In-memory mock database for hackathon demo.
Simulates MongoDB with realistic seed data for all 7 features.
"""
import uuid
from datetime import datetime, timedelta
import random

# --------------------------------------------------------------------------- #
# Seed helpers
# --------------------------------------------------------------------------- #
def _rnd_date(days_ago_min: int, days_ago_max: int) -> datetime:
    d = random.randint(days_ago_min, days_ago_max)
    return datetime.utcnow() - timedelta(days=d)

CATEGORIES = ["electronics", "clothing", "baby_products", "furniture",
              "sports", "books", "gaming", "toys"]

# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
USERS: dict[str, dict] = {
    "demo_user": {
        "_id": "demo_user",
        "name": "Alex Kumar",
        "email": "alex@example.com",
        "location": "Bangalore",
        "rating": 4.5,
        "green_credits": 350,
        "return_rate_pct": 18,
        "prime_member": True,
        "account_age_days": 730,
        "credit_history": [
            {"event": "buy_refurbished",      "points": 50,  "timestamp": _rnd_date(5,10)},
            {"event": "donate_product",        "points": 60,  "timestamp": _rnd_date(10,20)},
            {"event": "sell_unused_p2p",       "points": 40,  "timestamp": _rnd_date(20,30)},
            {"event": "choose_recycle",        "points": 25,  "timestamp": _rnd_date(30,40)},
            {"event": "upload_product_images", "points": 10,  "timestamp": _rnd_date(40,50)},
            {"event": "complete_p2p_exchange", "points": 30,  "timestamp": _rnd_date(50,60)},
        ],
    },
    "seller_01": {
        "_id": "seller_01", "name": "Priya Sharma", "email": "priya@example.com",
        "location": "Mumbai", "rating": 4.8, "green_credits": 180,
        "prime_member": True, "account_age_days": 900, "credit_history": [],
    },
    "seller_02": {
        "_id": "seller_02", "name": "Rahul Singh", "email": "rahul@example.com",
        "location": "Delhi", "rating": 4.2, "green_credits": 90,
        "prime_member": False, "account_age_days": 400, "credit_history": [],
    },
}

# --------------------------------------------------------------------------- #
# Refurbished Products
# --------------------------------------------------------------------------- #
REFURBISHED_PRODUCTS: list[dict] = [
    {
        "product_id": "REF001", "name": "MacBook Air M1 (Refurbished)",
        "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
        "category": "electronics", "refurb_price": 65000, "original_price": 95000,
        "vision_grade": "A", "repair_count": 0, "warranty_months_remaining": 6,
        "warranty_months_total": 12, "battery_health_pct": 91, "seller_rating": 4.8,
        "seller_id": "seller_01",
    },
    {
        "product_id": "REF002", "name": "Sony WH-1000XM4 Headphones",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        "category": "electronics", "refurb_price": 14500, "original_price": 26000,
        "vision_grade": "B", "repair_count": 1, "warranty_months_remaining": 3,
        "warranty_months_total": 12, "battery_health_pct": 85, "seller_rating": 4.5,
        "seller_id": "seller_02",
    },
    {
        "product_id": "REF003", "name": "Dyson V11 Vacuum (Certified Refurb)",
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
        "category": "electronics", "refurb_price": 28000, "original_price": 44000,
        "vision_grade": "A", "repair_count": 0, "warranty_months_remaining": 9,
        "warranty_months_total": 12, "battery_health_pct": 96, "seller_rating": 4.9,
        "seller_id": "seller_01",
    },
    {
        "product_id": "REF004", "name": "Lego Technic Set (Complete)",
        "image": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=400",
        "category": "toys", "refurb_price": 3200, "original_price": 5500,
        "vision_grade": "B", "repair_count": 0, "warranty_months_remaining": 0,
        "warranty_months_total": 0, "battery_health_pct": 100, "seller_rating": 4.3,
        "seller_id": "seller_02",
    },
    {
        "product_id": "REF005", "name": "Yoga Mat + Resistance Bands Kit",
        "image": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400",
        "category": "sports", "refurb_price": 900, "original_price": 1800,
        "vision_grade": "A", "repair_count": 0, "warranty_months_remaining": 0,
        "warranty_months_total": 0, "battery_health_pct": 100, "seller_rating": 4.7,
        "seller_id": "seller_01",
    },
    {
        "product_id": "REF006", "name": "Kindle Paperwhite 11th Gen",
        "image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400",
        "category": "electronics", "refurb_price": 7500, "original_price": 13999,
        "vision_grade": "A", "repair_count": 0, "warranty_months_remaining": 4,
        "warranty_months_total": 12, "battery_health_pct": 89, "seller_rating": 4.6,
        "seller_id": "seller_02",
    },
]

# --------------------------------------------------------------------------- #
# Orders
# --------------------------------------------------------------------------- #
ORDERS: list[dict] = [
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "product_id": "P100", "product_name": "Nike Running Shoes",
        "product_category": "clothing", "product_color": "Red", "product_size": "10",
        "purchase_date": _rnd_date(15, 20), "status": "returned",
        "price": 5500, "product_type": "new",
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "product_id": "P101", "product_name": "Samsung Galaxy Watch",
        "product_category": "electronics", "purchase_date": _rnd_date(30, 35),
        "status": "delivered", "price": 18000, "product_type": "new",
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "product_id": "REF001", "product_name": "MacBook Air M1 (Refurbished)",
        "product_category": "electronics", "purchase_date": _rnd_date(45, 50),
        "status": "delivered", "price": 65000, "product_type": "refurbished",
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "product_id": "P102", "product_name": "Cotton Kurta Set",
        "product_category": "clothing", "product_size": "M",
        "purchase_date": _rnd_date(60, 65), "status": "returned",
        "price": 1200, "product_type": "new",
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "seller_01",
        "product_id": "P200", "product_name": "Baby Stroller - Maxi Cosi",
        "product_category": "baby_products", "purchase_date": _rnd_date(10, 14),
        "status": "delivered", "price": 18000, "product_type": "new",
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "seller_02",
        "product_id": "P201", "product_name": "Fisher-Price Baby Gym",
        "product_category": "baby_products", "purchase_date": _rnd_date(8, 12),
        "status": "delivered", "price": 3500, "product_type": "new",
    },
]

# --------------------------------------------------------------------------- #
# Lifecycle Events
# --------------------------------------------------------------------------- #
LIFECYCLE_EVENTS: list[dict] = [
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "product_id": "P100",
        "input": {"category": "clothing", "return_reason": "size_issue"},
        "result": {"action": "exchange_marketplace", "label": "Exchange Marketplace"},
        "created_at": _rnd_date(5, 10),
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "product_id": "P201",
        "input": {"category": "electronics", "return_reason": "defective"},
        "result": {"action": "refurbish", "label": "Send for Refurbishment"},
        "created_at": _rnd_date(10, 15),
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "product_id": "P202",
        "input": {"category": "baby_products"},
        "result": {"action": "donate", "label": "Donate to NGO"},
        "created_at": _rnd_date(15, 20),
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "product_id": "P203",
        "input": {"category": "electronics"},
        "result": {"action": "resell_certified", "label": "Certified Refurbished"},
        "created_at": _rnd_date(20, 25),
    },
]

# --------------------------------------------------------------------------- #
# P2P Requests & Listings
# --------------------------------------------------------------------------- #
P2P_REQUESTS: list[dict] = []
P2P_LISTINGS: list[dict] = []

# --------------------------------------------------------------------------- #
# Notifications
# --------------------------------------------------------------------------- #
NOTIFICATIONS: list[dict] = [
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "type": "p2p_sell_opportunity",
        "title": "Someone wants to buy your product!",
        "body": "Budget: ₹8,000 for baby_products.",
        "read": False, "created_at": _rnd_date(0, 1),
    },
    {
        "_id": str(uuid.uuid4()), "user_id": "demo_user",
        "type": "green_credit",
        "title": "🌿 Green Credits Awarded!",
        "body": "+50 credits for buying refurbished.",
        "read": False, "created_at": _rnd_date(1, 2),
    },
]

# --------------------------------------------------------------------------- #
# Return signals per product
# --------------------------------------------------------------------------- #
RETURN_SIGNALS: dict[str, dict] = {
    "P100": {"product_id": "P100", "return_rate_pct": 42,
             "top_reasons": ["size_issue", "color_mismatch", "poor_quality"]},
    "P102": {"product_id": "P102", "return_rate_pct": 38,
             "top_reasons": ["size_issue", "not_as_described"]},
}

# --------------------------------------------------------------------------- #
# Cart events
# --------------------------------------------------------------------------- #
CART_EVENTS: list[dict] = [
    {"user_id": "demo_user", "event": "return_avoided", "created_at": _rnd_date(5, 10)},
    {"user_id": "demo_user", "event": "return_avoided", "created_at": _rnd_date(20, 25)},
]

# --------------------------------------------------------------------------- #
# Product ratings (for collaborative filtering)
# --------------------------------------------------------------------------- #
PRODUCT_RATINGS: list[dict] = []

# --------------------------------------------------------------------------- #
# Simple accessor helpers (mimic PyMongo-style)
# --------------------------------------------------------------------------- #
class _Collection:
    """Minimal in-memory collection with find/insert/update helpers."""
    def __init__(self, data: list):
        self._data = data

    def find(self, query: dict = None, projection: dict = None):
        results = [r.copy() for r in self._data]
        if query:
            results = [r for r in results if self._matches(r, query)]
        return _Cursor(results)

    def find_one(self, query: dict = None, projection: dict = None):
        for r in self._data:
            if not query or self._matches(r, query):
                return r.copy()
        return None

    def insert_one(self, doc: dict):
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        self._data.append(doc.copy())
        return doc["_id"]

    def insert_many(self, docs: list):
        for doc in docs:
            self.insert_one(doc)

    def delete_many(self, query: dict):
        self._data = [r for r in self._data if not self._matches(r, query)]

    def update_one(self, query: dict, update: dict):
        for r in self._data:
            if self._matches(r, query):
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        r[k] = r.get(k, 0) + v
                if "$set" in update:
                    for k, v in update["$set"].items():
                        r[k] = v
                if "$push" in update:
                    for k, v in update["$push"].items():
                        r.setdefault(k, []).append(v)
                break

    def update_many(self, query: dict, update: dict):
        for r in self._data:
            if self._matches(r, query):
                if "$set" in update:
                    for k, v in update["$set"].items():
                        r[k] = v

    def count_documents(self, query: dict = None):
        if not query:
            return len(self._data)
        return sum(1 for r in self._data if self._matches(r, query))

    def distinct(self, field: str, query: dict = None):
        data = self._data
        if query:
            data = [r for r in data if self._matches(r, query)]
        return list({r.get(field) for r in data if field in r})

    def aggregate(self, pipeline: list):
        # Minimal: only handle $match and $limit
        results = [r.copy() for r in self._data]
        for stage in pipeline:
            if "$match" in stage:
                q = stage["$match"]
                results = [r for r in results if self._matches(r, q)]
            elif "$limit" in stage:
                results = results[:stage["$limit"]]
        return results

    def _matches(self, record: dict, query: dict) -> bool:
        for key, val in query.items():
            if key == "$or":
                if not any(self._matches(record, sub) for sub in val):
                    return False
                continue
            parts = key.split(".")
            v = record
            for p in parts:
                if isinstance(v, dict):
                    v = v.get(p)
                else:
                    v = None
                    break
            if isinstance(val, dict):
                for op, operand in val.items():
                    if op == "$gte" and not (v is not None and v >= operand):
                        return False
                    if op == "$lte" and not (v is not None and v <= operand):
                        return False
                    if op == "$in" and v not in operand:
                        return False
                    if op == "$nin" and v in operand:
                        return False
                    if op == "$ne" and v == operand:
                        return False
                    if op == "$exists" and (val["$exists"] != (v is not None)):
                        return False
            else:
                if v != val:
                    return False
        return True


class _Cursor:
    def __init__(self, data: list):
        self._data = data

    def sort(self, key: str, direction: int = 1):
        self._data.sort(key=lambda r: r.get(key, 0), reverse=(direction == -1))
        return self

    def limit(self, n: int):
        self._data = self._data[:n]
        return self

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


# --------------------------------------------------------------------------- #
# Database object
# --------------------------------------------------------------------------- #
class _DB:
    users               = _Collection(list(USERS.values()))
    orders              = _Collection(ORDERS)
    refurbished_products = _Collection(REFURBISHED_PRODUCTS)
    lifecycle_events    = _Collection(LIFECYCLE_EVENTS)
    p2p_requests        = _Collection(P2P_REQUESTS)
    p2p_listings        = _Collection(P2P_LISTINGS)
    notifications       = _Collection(NOTIFICATIONS)
    return_signals      = _Collection(list(RETURN_SIGNALS.values()))
    cart_events         = _Collection(CART_EVENTS)
    product_ratings     = _Collection(PRODUCT_RATINGS)
    p2p_chats           = _Collection([])


db = _DB()
