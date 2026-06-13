"""Feature 5 — P2P Marketplace router."""
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
from db import db
from utils.auth import get_current_user
from agents.p2p_ranker import rank_sellers
import uuid

router = APIRouter(prefix="/p2p", tags=["p2p"])

CATEGORY_LIFECYCLE = {
    "baby_products":     {"min_months": 6,  "max_months": 36},
    "baby_clothing":     {"min_months": 3,  "max_months": 18},
    "fitness_equipment": {"min_months": 12, "max_months": 48},
    "electronics":       {"min_months": 18, "max_months": 60},
    "maternity":         {"min_months": 6,  "max_months": 12},
    "seasonal_clothing": {"min_months": 8,  "max_months": 24},
    "sports_gear":       {"min_months": 12, "max_months": 48},
    "gaming":            {"min_months": 12, "max_months": 36},
    "toys":              {"min_months": 6,  "max_months": 36},
    "books":             {"min_months": 1,  "max_months": 120},
    "default":           {"min_months": 12, "max_months": 48},
}


class P2PRequest(BaseModel):
    product_id: str = ""
    category: str
    max_budget: float
    condition: str = "any"


class SellerOptIn(BaseModel):
    request_id: str
    listing_price: float
    condition: str
    description: str


@router.post("/request")
async def create_p2p_request(
    req: P2PRequest,
    bg: BackgroundTasks,
    user=Depends(get_current_user),
):
    request_id = str(uuid.uuid4())
    window     = CATEGORY_LIFECYCLE.get(req.category, CATEGORY_LIFECYCLE["default"])
    now        = datetime.utcnow()
    after      = now - timedelta(days=window["max_months"] * 30)
    before     = now - timedelta(days=window["min_months"] * 30)

    db.p2p_requests.insert_one({
        "_id": request_id, "buyer_id": user["user_id"],
        "category": req.category, "max_budget": req.max_budget,
        "condition": req.condition, "status": "open", "created_at": now,
    })

    # Find potential sellers from orders
    sellers = list(db.orders.find({
        "product_category": req.category,
        "status": {"$in": ["delivered", "completed"]},
        "user_id": {"$ne": user["user_id"]},
    }))

    # Enrich with user info
    enriched = []
    for s in sellers[:20]:
        seller_info = db.users.find_one({"_id": s.get("user_id")}) or {}
        enriched.append({**s, "seller_info": {
            "name":   seller_info.get("name", "Anonymous"),
            "rating": seller_info.get("rating", 4.0),
            "location": seller_info.get("location", "India"),
        }})

    ranked = await rank_sellers(enriched, req.model_dump(), user)

    # Store in-app notifications for sellers
    bg.add_task(_notify_sellers, ranked[:5], request_id, req)

    return {
        "request_id":        request_id,
        "potential_matches": len(sellers),
        "top_preview":       ranked[:3],
        "message": f"Notifying {min(len(sellers), 5)} potential sellers!",
    }


@router.post("/seller/optin")
async def seller_opt_in(optin: SellerOptIn, user=Depends(get_current_user)):
    req_doc = db.p2p_requests.find_one({"_id": optin.request_id})
    if not req_doc:
        return {"error": "Request not found"}
    listing_id = str(uuid.uuid4())
    db.p2p_listings.insert_one({
        "_id":        listing_id,
        "request_id": optin.request_id,
        "seller_id":  user["user_id"],
        "buyer_id":   req_doc["buyer_id"],
        "price":      optin.listing_price,
        "condition":  optin.condition,
        "description": optin.description,
        "status":     "pending_acceptance",
        "created_at": datetime.utcnow(),
    })
    # Notify buyer
    db.notifications.insert_one({
        "user_id": req_doc["buyer_id"], "type": "p2p_seller_found",
        "title": "🎉 A seller matched your request!",
        "body":  f"Price offered: ₹{optin.listing_price:,.0f}. Condition: {optin.condition}.",
        "read": False, "created_at": datetime.utcnow(),
    })
    return {"listing_id": listing_id, "status": "pending_acceptance"}


@router.get("/matches/{request_id}")
async def get_matches(request_id: str, user=Depends(get_current_user)):
    listings = list(db.p2p_listings.find({"request_id": request_id}))
    for l in listings:
        l.pop("_id", None)
    return {"listings": listings}


@router.get("/my-requests")
async def my_requests(user=Depends(get_current_user)):
    requests = list(db.p2p_requests.find({"buyer_id": user["user_id"]}))
    for r in requests:
        r.pop("_id", None)
        r["created_at"] = str(r.get("created_at", ""))
    return {"requests": requests}


async def _notify_sellers(sellers, request_id, req):
    for s in sellers:
        uid = s.get("user_id")
        if uid:
            db.notifications.insert_one({
                "user_id": uid, "type": "p2p_sell_opportunity",
                "title": "💰 Someone wants to buy your product!",
                "body":  f"Budget: ₹{req.max_budget:,.0f} for {req.category}.",
                "request_id": request_id, "read": False,
                "created_at": datetime.utcnow(),
            })
