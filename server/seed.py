"""
ReLife AI — Seed MongoDB with 200 synthetic users and related data.
Run: python seed.py
"""
import random
import uuid
from datetime import datetime, timedelta
from config import settings

if not settings.MONGO_URI:
    print("❌ MONGO_URI not set in .env")
    exit(1)

from pymongo import MongoClient

client = MongoClient(settings.MONGO_URI)
database = client.get_database("relife_ai")

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
rng = random.Random(42)

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Ananya", "Diya", "Myra", "Sara", "Aarohi", "Anika",
    "Priya", "Isha", "Kavya", "Riya", "Rahul", "Rohan", "Amit", "Vikram",
    "Neha", "Pooja", "Sneha", "Divya", "Meera", "Tanvi", "Kiran", "Raj",
    "Suresh", "Mahesh", "Lakshmi", "Gauri", "Harsh", "Yash", "Nikhil", "Pranav"
]
LAST_NAMES = [
    "Kumar", "Sharma", "Singh", "Patel", "Gupta", "Reddy", "Nair", "Joshi",
    "Verma", "Iyer", "Chopra", "Malhotra", "Mehta", "Shah", "Rao", "Das",
    "Pillai", "Menon", "Chauhan", "Tiwari", "Bansal", "Aggarwal", "Saxena",
    "Bhat", "Kulkarni", "Deshmukh", "Patil", "Mishra", "Pandey", "Dubey"
]
CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Indore",
    "Kochi", "Coimbatore", "Nagpur", "Bhopal", "Noida", "Gurgaon"
]
CATEGORIES = [
    "electronics", "clothing", "baby_products", "furniture",
    "sports", "books", "gaming", "toys"
]
RETURN_REASONS = [
    "defective", "wrong_item", "size_issue", "changed_mind",
    "better_price", "not_as_described"
]
PRODUCT_NAMES = {
    "electronics": ["Samsung Galaxy S24", "Sony WH-1000XM5", "MacBook Air M2", "iPad Air",
                    "JBL Flip 6", "Kindle Paperwhite", "Logitech MX Master 3", "AirPods Pro"],
    "clothing": ["Nike Air Max", "Levi's 501", "Adidas Ultraboost", "Puma T-Shirt",
                 "H&M Jacket", "Zara Dress", "Allen Solly Shirt", "Van Heusen Blazer"],
    "baby_products": ["Baby Stroller", "Diaper Bag", "Baby Monitor", "Car Seat",
                      "High Chair", "Baby Swing", "Playmat", "Baby Carrier"],
    "furniture": ["IKEA Desk", "Office Chair", "Bookshelf", "Sofa Set",
                  "Dining Table", "Bean Bag", "TV Stand", "Shoe Rack"],
    "sports": ["Yoga Mat", "Dumbbells Set", "Resistance Bands", "Cricket Bat",
               "Badminton Racket", "Running Shoes", "Fitness Tracker", "Cycling Gloves"],
    "books": ["Atomic Habits", "Sapiens", "The Alchemist", "Rich Dad Poor Dad",
              "Thinking Fast and Slow", "Deep Work", "Zero to One", "The Lean Startup"],
    "gaming": ["PS5 Controller", "Nintendo Switch", "Gaming Mouse", "Mechanical Keyboard",
               "Gaming Headset", "Xbox Game Pass", "Gaming Chair", "VR Headset"],
    "toys": ["Lego Technic", "Hot Wheels Set", "Nerf Gun", "Board Game Collection",
             "Rubik's Cube", "Drone", "RC Car", "Puzzle Set"],
}


def rnd_date(days_ago_min: int, days_ago_max: int) -> datetime:
    d = rng.randint(days_ago_min, days_ago_max)
    return datetime.utcnow() - timedelta(days=d)


# --------------------------------------------------------------------------- #
# Generate Users (200)
# --------------------------------------------------------------------------- #
def generate_users(n=200):
    users = []
    # Always include demo_user first (the default auth user)
    users.append({
        "_id": "demo_user",
        "name": "Alex Kumar",
        "email": "alex@relife.demo",
        "location": "Bangalore",
        "rating": 4.5,
        "green_credits": 420,
        "return_rate_pct": 18,
        "prime_member": True,
        "account_age_days": 730,
        "credit_history": [
            {"event": "buy_refurbished", "points": 50, "timestamp": rnd_date(5, 10)},
            {"event": "donate_product", "points": 60, "timestamp": rnd_date(10, 20)},
            {"event": "sell_unused_p2p", "points": 40, "timestamp": rnd_date(20, 30)},
            {"event": "choose_recycle", "points": 25, "timestamp": rnd_date(30, 40)},
            {"event": "upload_product_images", "points": 10, "timestamp": rnd_date(40, 50)},
            {"event": "complete_p2p_exchange", "points": 30, "timestamp": rnd_date(50, 60)},
            {"event": "buy_refurbished", "points": 50, "timestamp": rnd_date(2, 5)},
            {"event": "return_avoided", "points": 20, "timestamp": rnd_date(1, 3)},
        ],
    })
    for i in range(1, n):
        uid = f"user_{i:04d}"
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        users.append({
            "_id": uid,
            "name": name,
            "email": f"{uid}@relife.demo",
            "location": rng.choice(CITIES),
            "rating": round(rng.uniform(3.0, 5.0), 1),
            "green_credits": rng.randint(0, 600),
            "return_rate_pct": rng.randint(5, 45),
            "prime_member": rng.random() > 0.4,
            "account_age_days": rng.randint(30, 1500),
            "credit_history": [],
        })
    return users


# --------------------------------------------------------------------------- #
# Generate Orders (1000)
# --------------------------------------------------------------------------- #
def generate_orders(users, n=1000):
    orders = []
    # Ensure demo_user has a good mix of orders
    demo_orders = [
        {"cat": "electronics", "status": "delivered", "ptype": "refurbished"},
        {"cat": "electronics", "status": "delivered", "ptype": "refurbished"},
        {"cat": "clothing", "status": "returned", "ptype": "new"},
        {"cat": "clothing", "status": "returned", "ptype": "new"},
        {"cat": "baby_products", "status": "delivered", "ptype": "new"},
        {"cat": "electronics", "status": "delivered", "ptype": "refurbished"},
        {"cat": "sports", "status": "delivered", "ptype": "new"},
        {"cat": "gaming", "status": "delivered", "ptype": "refurbished"},
        {"cat": "toys", "status": "delivered", "ptype": "new"},
        {"cat": "books", "status": "delivered", "ptype": "new"},
    ]
    for i, d in enumerate(demo_orders):
        orders.append({
            "_id": str(uuid.uuid4()),
            "user_id": "demo_user",
            "product_id": f"P{2000 + i}",
            "product_name": rng.choice(PRODUCT_NAMES[d["cat"]]),
            "product_category": d["cat"],
            "purchase_date": rnd_date(10 + i * 15, 20 + i * 15),
            "status": d["status"],
            "price": rng.randint(500, 40000),
            "product_type": d["ptype"],
        })

    for _ in range(n):
        user = rng.choice(users)
        cat = rng.choice(CATEGORIES)
        product_name = rng.choice(PRODUCT_NAMES[cat])
        status = rng.choices(
            ["delivered", "returned", "completed"],
            weights=[60, 25, 15]
        )[0]
        orders.append({
            "_id": str(uuid.uuid4()),
            "user_id": user["_id"],
            "product_id": f"P{rng.randint(1000, 9999)}",
            "product_name": product_name,
            "product_category": cat,
            "purchase_date": rnd_date(5, 400),
            "status": status,
            "price": rng.randint(200, 50000),
            "product_type": rng.choices(["new", "refurbished"], weights=[75, 25])[0],
        })
    return orders


# --------------------------------------------------------------------------- #
# Generate Refurbished Products (50)
# --------------------------------------------------------------------------- #
def generate_refurbished(users, n=50):
    products = []
    grades = ["A", "A", "A", "B", "B", "C"]  # bias toward good condition
    for i in range(n):
        cat = rng.choice(CATEGORIES)
        original_price = rng.randint(1000, 80000)
        grade = rng.choice(grades)
        discount = {"A": 0.30, "B": 0.45, "C": 0.60}[grade]
        products.append({
            "product_id": f"REF{i:03d}",
            "name": f"{rng.choice(PRODUCT_NAMES[cat])} (Refurbished)",
            "image": f"https://picsum.photos/seed/{i}/400/300",
            "category": cat,
            "refurb_price": int(original_price * (1 - discount)),
            "original_price": original_price,
            "vision_grade": grade,
            "repair_count": rng.randint(0, 3),
            "warranty_months_remaining": rng.randint(0, 12),
            "warranty_months_total": 12,
            "battery_health_pct": rng.randint(70, 100),
            "seller_rating": round(rng.uniform(3.5, 5.0), 1),
            "seller_id": rng.choice(users)["_id"],
        })
    return products


# --------------------------------------------------------------------------- #
# Generate Lifecycle Events (300)
# --------------------------------------------------------------------------- #
def generate_lifecycle_events(users, n=300):
    actions = [
        {"action": "resell_certified", "label": "Certified Refurbished"},
        {"action": "refurbish", "label": "Send for Refurbishment"},
        {"action": "exchange_marketplace", "label": "Exchange Marketplace"},
        {"action": "donate", "label": "Donate to NGO"},
        {"action": "recycle", "label": "Recycle"},
    ]
    events = []
    # demo_user gets 15 lifecycle events for a good dashboard
    demo_actions = [
        actions[0], actions[0], actions[1], actions[1], actions[2],
        actions[3], actions[3], actions[3], actions[4], actions[4],
        actions[0], actions[1], actions[2], actions[3], actions[0],
    ]
    for i, action in enumerate(demo_actions):
        events.append({
            "_id": str(uuid.uuid4()),
            "user_id": "demo_user",
            "product_id": f"P{3000 + i}",
            "input": {
                "category": rng.choice(CATEGORIES),
                "return_reason": rng.choice(RETURN_REASONS),
            },
            "result": action,
            "created_at": rnd_date(1 + i * 5, 5 + i * 5),
        })
    for _ in range(n):
        user = rng.choice(users)
        cat = rng.choice(CATEGORIES)
        action = rng.choice(actions)
        events.append({
            "_id": str(uuid.uuid4()),
            "user_id": user["_id"],
            "product_id": f"P{rng.randint(1000, 9999)}",
            "input": {
                "category": cat,
                "return_reason": rng.choice(RETURN_REASONS),
            },
            "result": action,
            "created_at": rnd_date(1, 180),
        })
    return events


# --------------------------------------------------------------------------- #
# Generate Return Signals (100 products)
# --------------------------------------------------------------------------- #
def generate_return_signals(n=100):
    signals = []
    for i in range(n):
        signals.append({
            "_id": f"P{1000 + i}",
            "product_id": f"P{1000 + i}",
            "return_rate_pct": rng.randint(5, 55),
            "top_reasons": rng.sample(RETURN_REASONS, k=rng.randint(1, 3)),
        })
    return signals


# --------------------------------------------------------------------------- #
# Generate Cart Events (200)
# --------------------------------------------------------------------------- #
def generate_cart_events(users, n=200):
    events = []
    # demo_user gets 8 return_avoided events
    for i in range(8):
        events.append({
            "_id": str(uuid.uuid4()),
            "user_id": "demo_user",
            "event": "return_avoided",
            "created_at": rnd_date(1 + i * 5, 5 + i * 5),
        })
    for _ in range(n):
        user = rng.choice(users)
        events.append({
            "_id": str(uuid.uuid4()),
            "user_id": user["_id"],
            "event": "return_avoided",
            "created_at": rnd_date(1, 90),
        })
    return events


# --------------------------------------------------------------------------- #
# Generate Product Ratings (500)
# --------------------------------------------------------------------------- #
def generate_ratings(users, products, n=500):
    ratings = []
    for _ in range(n):
        user = rng.choice(users)
        product = rng.choice(products)
        ratings.append({
            "user_id": user["_id"],
            "product_id": product["product_id"],
            "rating": rng.randint(1, 5),
        })
    return ratings


# --------------------------------------------------------------------------- #
# Generate Notifications (50)
# --------------------------------------------------------------------------- #
def generate_notifications(users, n=50):
    types = [
        ("p2p_sell_opportunity", "💰 Someone wants to buy your product!", "Budget: ₹{} for {}."),
        ("green_credit", "🌿 Green Credits Awarded!", "+{} credits for {}."),
        ("lifecycle_complete", "♻️ Product Lifecycle Complete", "Your {} was {}."),
    ]
    notifs = []
    for _ in range(n):
        user = rng.choice(users)
        ntype, title, body_tpl = rng.choice(types)
        cat = rng.choice(CATEGORIES)
        notifs.append({
            "_id": str(uuid.uuid4()),
            "user_id": user["_id"],
            "type": ntype,
            "title": title,
            "body": body_tpl.format(rng.randint(20, 100), cat),
            "read": rng.random() > 0.6,
            "created_at": rnd_date(0, 30),
        })
    return notifs


# --------------------------------------------------------------------------- #
# SEED
# --------------------------------------------------------------------------- #
def seed():
    print("🌱 Seeding MongoDB Atlas with synthetic data...")

    users = generate_users(200)
    orders = generate_orders(users, 1000)
    refurbished = generate_refurbished(users, 50)
    lifecycle = generate_lifecycle_events(users, 300)
    signals = generate_return_signals(100)
    cart_events = generate_cart_events(users, 200)
    ratings = generate_ratings(users, refurbished, 500)
    notifications = generate_notifications(users, 50)

    # Clear and insert
    collections = {
        "users": users,
        "orders": orders,
        "refurbished_products": refurbished,
        "lifecycle_events": lifecycle,
        "return_signals": signals,
        "cart_events": cart_events,
        "product_ratings": ratings,
        "notifications": notifications,
    }

    for name, data in collections.items():
        database[name].delete_many({})
        if data:
            database[name].insert_many(data)
        print(f"   ✅ {name}: {len(data)} documents")

    print(f"\n🎉 Database seeded successfully!")
    print(f"   200 users, 1000 orders, 50 refurbished products")
    print(f"   300 lifecycle events, 500 ratings, 100 return signals")
    print(f"   Database: relife_ai @ MongoDB Atlas")


if __name__ == "__main__":
    seed()
