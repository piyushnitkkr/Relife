"""Feature 7 — Sustainability Dashboard router."""
from fastapi import APIRouter, Depends
from db import db
from utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

CO2_PER_AVOIDED_RETURN_KG  = 2.5
CO2_PER_REFURBISHED_BUY_KG = 4.0
CO2_PER_DONATED_ITEM_KG    = 1.8
CO2_PER_RECYCLED_ITEM_KG   = 1.2


@router.get("/sustainability")
async def get_sustainability_stats(user=Depends(get_current_user)):
    uid = user["user_id"]

    products_saved = db.lifecycle_events.count_documents({
        "user_id": uid,
        "result.action": {"$in": [
            "resell_certified", "refurbish", "donate", "exchange_marketplace"
        ]},
    })
    returns_avoided = db.cart_events.count_documents(
        {"user_id": uid, "event": "return_avoided"}
    )
    refurb_bought = db.orders.count_documents(
        {"user_id": uid, "product_type": "refurbished"}
    )
    items_donated  = db.lifecycle_events.count_documents(
        {"user_id": uid, "result.action": "donate"}
    )
    items_recycled = db.lifecycle_events.count_documents(
        {"user_id": uid, "result.action": "recycle"}
    )
    p2p_completed = db.p2p_listings.count_documents({
        "$or": [{"seller_id": uid}, {"buyer_id": uid}],
        "status": "completed",
    })

    co2_saved = round(
        returns_avoided  * CO2_PER_AVOIDED_RETURN_KG +
        refurb_bought    * CO2_PER_REFURBISHED_BUY_KG +
        items_donated    * CO2_PER_DONATED_ITEM_KG +
        items_recycled   * CO2_PER_RECYCLED_ITEM_KG,
        1,
    )

    user_doc = db.users.find_one({"_id": uid}) or {}
    credits  = user_doc.get("green_credits", 0)

    return {
        "products_saved":   products_saved,
        "co2_saved_kg":     co2_saved,
        "trees_equivalent": round(co2_saved / 21, 2),
        "items_donated":    items_donated,
        "items_recycled":   items_recycled,
        "p2p_exchanges":    p2p_completed,
        "returns_avoided":  returns_avoided,
        "refurb_bought":    refurb_bought,
        "green_credits":    credits,
        "impact_level": (
            "🌍 Planet Hero"  if products_saved >= 20 else
            "🌳 Eco Champion" if products_saved >= 10 else
            "🌿 Green Starter"
        ),
    }
