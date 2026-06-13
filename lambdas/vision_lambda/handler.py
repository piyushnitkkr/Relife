"""
AWS Lambda — Vision Grader using Amazon Rekognition.
Triggered via API Gateway. Free: 5,000 images/month.
"""
import json
import boto3
import base64

rekognition = boto3.client("rekognition")
s3 = boto3.client("s3")

DAMAGE_LABELS = {
    "Scratch", "Crack", "Dent", "Broken", "Damaged",
    "Worn", "Stain", "Tear", "Burn", "Chip"
}
ACCESSORY_LABELS = {
    "Cable", "Charger", "Box", "Manual", "Adapter", "Remote"
}
GRADE_THRESHOLDS = [
    (0,  10,  "A", "Like New",      4, "Resell as Certified Refurbished"),
    (10, 30,  "B", "Minor Wear",    3, "Light Refurbishment"),
    (30, 60,  "C", "Refurbishable", 2, "Send for Repair"),
    (60, 100, "D", "Recycle",       1, "Recycle"),
]


def lambda_handler(event, context):
    """
    Expects JSON body with:
      - image_keys: list of S3 keys  OR
      - image_base64: single base64-encoded image
    """
    body = json.loads(event.get("body", "{}"))
    bucket = body.get("bucket", "relife-ai-assets")
    image_keys = body.get("image_keys", [])
    image_b64 = body.get("image_base64")

    all_damage_scores = []
    accessories_found = []

    # Process S3 images
    for key in image_keys[:5]:
        response = rekognition.detect_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MaxLabels=30,
            MinConfidence=50,
        )
        damage_conf, acc = _process_labels(response.get("Labels", []))
        all_damage_scores.append(damage_conf)
        accessories_found.extend(acc)

    # Process base64 image (direct upload)
    if image_b64 and not image_keys:
        image_bytes = base64.b64decode(image_b64)
        response = rekognition.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=30,
            MinConfidence=50,
        )
        damage_conf, acc = _process_labels(response.get("Labels", []))
        all_damage_scores.append(damage_conf)
        accessories_found.extend(acc)

    if not all_damage_scores:
        return _response(400, {"error": "No images provided"})

    avg_damage = sum(all_damage_scores) / len(all_damage_scores)

    grade_letter, grade_label, grade_numeric, recommendation = "A", "Like New", 4, "Resell"
    for lo, hi, letter, label, numeric, rec in GRADE_THRESHOLDS:
        if lo <= avg_damage < hi:
            grade_letter, grade_label, grade_numeric, recommendation = letter, label, numeric, rec
            break

    result = {
        "grade": grade_letter,
        "grade_label": grade_label,
        "grade_numeric": grade_numeric,
        "confidence": round(100 - avg_damage, 1),
        "damage_score_pct": round(avg_damage, 1),
        "accessories_detected": list(set(accessories_found)),
        "recommendation": recommendation,
        "images_analyzed": len(all_damage_scores),
    }
    return _response(200, result)


def _process_labels(labels):
    """Extract damage score and accessories from Rekognition labels."""
    label_names = {l["Name"] for l in labels}
    acc_labels = list(label_names & ACCESSORY_LABELS)
    damage_conf = max(
        (l["Confidence"] for l in labels if l["Name"] in DAMAGE_LABELS),
        default=0,
    )
    return damage_conf, acc_labels


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
