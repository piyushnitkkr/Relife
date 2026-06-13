"""
AWS Lambda — Lifecycle Classifier (XGBoost inference).
Triggered via API Gateway or SQS.
"""
import json
import pickle
import numpy as np
import boto3
from pathlib import Path

# Model is bundled in the deployment package at /var/task/model/
MODEL_PATH = Path("/var/task/model/lifecycle_xgb.pkl")

# Try loading the model; if not available, use heuristic fallback
_model = None
try:
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
except Exception:
    pass

LABEL_MAP = {
    0: {"action": "resell_certified",     "label": "Certified Refurbished"},
    1: {"action": "refurbish",            "label": "Send for Refurbishment"},
    2: {"action": "exchange_marketplace", "label": "Exchange Marketplace"},
    3: {"action": "donate",               "label": "Donate to NGO"},
    4: {"action": "recycle",              "label": "Recycle"},
}

CATEGORY_ENCODING = {
    "electronics": 0, "clothing": 1, "baby_products": 2,
    "furniture": 3, "sports": 4, "books": 5, "other": 6,
    "gaming": 7, "toys": 8,
}

RETURN_REASON_ENCODING = {
    "defective": 0, "wrong_item": 1, "size_issue": 2,
    "changed_mind": 3, "better_price": 4, "not_as_described": 5,
}

CREDITS = {
    "resell_certified": 50, "refurbish": 35,
    "exchange_marketplace": 30, "donate": 60, "recycle": 25,
}

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    features = np.array([[
        CATEGORY_ENCODING.get(body.get("category", "other"), 6),
        RETURN_REASON_ENCODING.get(body.get("return_reason", "changed_mind"), 3),
        min(body.get("product_age_days", 0), 1825) / 1825,
        min(body.get("return_frequency", 0), 10) / 10,
        min(body.get("repair_cost_estimate", 0), 5000) / 5000,
        body.get("vision_grade_numeric", 2) / 4,
        min(body.get("seller_reputation", 3.0), 5.0) / 5.0,
        1 if body.get("accessories_present", False) else 0,
        min(body.get("days_since_purchase", 0), 365) / 365,
    ]])

    if _model is not None:
        prediction = int(_model.predict(features)[0])
        probabilities = _model.predict_proba(features)[0]
        confidence = round(float(probabilities[prediction]) * 100, 1)
        all_scores = {
            LABEL_MAP[i]["label"]: round(float(p) * 100, 1)
            for i, p in enumerate(probabilities)
        }
    else:
        # Heuristic fallback
        grade = body.get("vision_grade_numeric", 2)
        if grade >= 3:
            prediction = 0
        elif grade >= 2:
            prediction = 1
        else:
            prediction = 4
        confidence = 75.0
        all_scores = {LABEL_MAP[i]["label"]: 20.0 for i in range(5)}
        all_scores[LABEL_MAP[prediction]["label"]] = confidence

    result = LABEL_MAP[prediction]
    credits = CREDITS.get(result["action"], 0)

    # Award credits in DynamoDB if user_id is provided
    user_id = body.get("user_id")
    if user_id and credits > 0:
        try:
            import os
            table_name = os.environ.get("DYNAMO_TABLE_NAME", "relife-user-credits")
            table = dynamodb.Table(table_name)
            table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="ADD green_credits :p",
                ExpressionAttributeValues={":p": credits},
            )
        except Exception as e:
            print(f"DynamoDB update failed: {e}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({
            "action": result["action"],
            "label": result["label"],
            "confidence": confidence,
            "all_scores": all_scores,
            "green_credits_awarded": credits,
        }),
    }
