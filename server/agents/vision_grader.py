"""
Vision Grader — Uses AWS Rekognition when configured, falls back to simulation.
Free Tier: 5,000 images/month.
"""
import hashlib
import random
from config import settings

try:
    import boto3
    _boto3_available = True
except ImportError:
    _boto3_available = False

DAMAGE_LABELS = {
    "Scratch", "Crack", "Dent", "Broken", "Damaged",
    "Worn", "Stain", "Tear", "Burn", "Chip"
}
ACCESSORY_LABELS = {
    "Cable", "Charger", "Box", "Manual", "Adapter", "Remote"
}

GRADE_THRESHOLDS = [
    (0,  10,  "A", "Like New",       4, "Resell as Certified Refurbished"),
    (10, 30,  "B", "Minor Wear",     3, "Light Refurbishment"),
    (30, 60,  "C", "Refurbishable",  2, "Send for Repair"),
    (60, 100, "D", "Recycle",        1, "Recycle"),
]

# Try to initialize Rekognition client
_rekognition = None
if _boto3_available:
    try:
        _rekognition = boto3.client("rekognition", region_name=settings.AWS_REGION)
        _rekognition.meta.service_model
    except Exception:
        _rekognition = None


def _use_real_rekognition() -> bool:
    return _rekognition is not None


def _analyze_with_rekognition(image_bytes: bytes) -> dict:
    """Call real AWS Rekognition detect_labels API."""
    response = _rekognition.detect_labels(
        Image={"Bytes": image_bytes},
        MaxLabels=30,
        MinConfidence=50
    )
    return {"Labels": response.get("Labels", [])}


def _simulate_rekognition(image_bytes: bytes) -> dict:
    """Deterministic simulation based on image content hash."""
    digest = hashlib.md5(image_bytes[:512]).hexdigest()
    seed = int(digest[:8], 16)
    rng = random.Random(seed)

    damage_score = rng.uniform(0, 55)
    detected_damage = []
    if damage_score > 10:
        detected_damage = rng.sample(list(DAMAGE_LABELS), k=rng.randint(1, 2))
    detected_acc = rng.sample(list(ACCESSORY_LABELS), k=rng.randint(0, 2))

    labels = [
        {"Name": l, "Confidence": rng.uniform(50, 95)}
        for l in detected_damage + detected_acc
    ]
    return {"Labels": labels}


async def grade_from_images(image_data_list: list) -> dict:
    """
    Grade from list of raw image bytes.
    Uses real Rekognition in production, simulation in dev.
    """
    all_damage_scores, accessories_found = [], []

    for img_bytes in image_data_list[:5]:
        if _use_real_rekognition():
            result = _analyze_with_rekognition(img_bytes)
        else:
            result = _simulate_rekognition(img_bytes)

        labels = result["Labels"]
        label_names = {l["Name"] for l in labels}
        acc_labels = label_names & ACCESSORY_LABELS

        damage_conf = max(
            (l["Confidence"] for l in labels if l["Name"] in DAMAGE_LABELS),
            default=0
        )
        all_damage_scores.append(damage_conf)
        if acc_labels:
            accessories_found.extend(list(acc_labels))

    avg_damage = (sum(all_damage_scores) / len(all_damage_scores)
                  if all_damage_scores else 5.0)

    grade_letter, grade_label, grade_numeric, recommendation = "A", "Like New", 4, "Resell"
    for lo, hi, letter, label, numeric, rec in GRADE_THRESHOLDS:
        if lo <= avg_damage < hi:
            grade_letter, grade_label, grade_numeric, recommendation = letter, label, numeric, rec
            break

    return {
        "grade":               grade_letter,
        "grade_label":         grade_label,
        "grade_numeric":       grade_numeric,
        "confidence":          round(100 - avg_damage, 1),
        "damage_score_pct":    round(avg_damage, 1),
        "accessories_detected": list(set(accessories_found)),
        "recommendation":      recommendation,
        "images_analyzed":     len(image_data_list),
        "engine":              "rekognition" if _use_real_rekognition() else "simulated",
    }
