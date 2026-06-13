"""Feature 4 — Green Credits System router."""
from fastapi import APIRouter, Depends
from db.mongo import db
from db.dynamo import dynamo_table
from utils.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/credits", tags=["credits"])

CREDIT_RULES = {
    # Earning
    "buy_refurbished":          50,
    "sell_unused_p2p":          40,
    "donate_product":           60,
    "choose_recycle":           25,
    "return_avoided":           20,
    "upload_product_images":    10,
    "complete_p2p_exchange":    30,
    # Redeeming (negative)
    "redeem_amazon_coupon_100": -100,
    "redeem_prime_discount":    -200,
    "redeem_carbon_offset":     -150,
}

CREDIT_TO_INR = 0.5


@router.post("/award/{event}")
async def award_credits(event: str, user=Depends(get_current_user)):
    points = CREDIT_RULES.get(event)
    if points is None or points < 0:
        return {"error": "Unknown or non-earning event"}

    db.users.update_one(
        {"_id": user["user_id"]},
        {"$inc":  {"green_credits": points},
         "$push": {"credit_history": {
             "event": event, "points": points, "timestamp": datetime.utcnow()
         }}}
    )
    dynamo_table.update_item(
        Key={"user_id": user["user_id"]},
        UpdateExpression="ADD green_credits :p",
        ExpressionAttributeValues={":p": points},
    )
    return {
        "awarded":   points,
        "event":     event,
        "inr_value": f"₹{points * CREDIT_TO_INR:.0f}",
        "message":   f"🌿 +{points} Green Credits earned!",
    }


@router.post("/redeem/{event}")
async def redeem_credits(event: str, user=Depends(get_current_user)):
    cost = abs(CREDIT_RULES.get(event, 0))
    if cost == 0:
        return {"error": "Unknown redemption event"}
    user_doc = db.users.find_one({"_id": user["user_id"]}) or {}
    balance  = user_doc.get("green_credits", 0)
    if balance < cost:
        return {"error": f"Insufficient credits. Need {cost}, have {balance}"}
    db.users.update_one({"_id": user["user_id"]}, {"$inc": {"green_credits": -cost}})
    uid_short = user["user_id"][:6].upper()
    return {
        "redeemed":    cost,
        "new_balance": balance - cost,
        "coupon_code": f"RELIFE-{uid_short}-{cost}",
    }


@router.get("/balance")
async def get_balance(user=Depends(get_current_user)):
    result  = dynamo_table.get_item(Key={"user_id": user["user_id"]})
    balance = int(result.get("Item", {}).get("green_credits", 0))
    return {
        "balance":   balance,
        "inr_value": f"₹{balance * CREDIT_TO_INR:.0f}",
        "tier": (
            "🌳 Eco Champion" if balance >= 500 else
            "🌿 Green Member" if balance >= 200 else
            "🌱 Getting Started"
        ),
        "history": (db.users.find_one({"_id": user["user_id"]}) or {})
                   .get("credit_history", [])[-10:],
    }
