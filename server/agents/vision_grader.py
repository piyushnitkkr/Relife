"""
Vision Grader — Simulates AWS Rekognition for hackathon demo.
Uses image metadata + random-seeded heuristics to produce realistic grades.
In production: replace _analyze_image() with actual rekognition.detect_labels() calls.
"""
import hashlib
import random
from pathlib import Path

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


def _simulate_rekognition(image_bytes: bytes) -> dict:
    """
    Deterministic simulation based on image content hash.
    Replaces real rekognition.detect_labels() call.
    """
    digest = hashlib.md5(image_bytes[:512]).hexdigest()
    seed   = int(digest[:8], 16)
    rng    = random.Random(seed)

    damage_score = rng.uniform(0, 55)      # bias toward good condition for demo
    detected_damage = []
    if damage_score > 10:
        detected_damage = rng.sample(list(DAMAGE_LABELS), k=rng.randint(1, 2))
    detected_acc = rng.sample(list(ACCESSORY_LABELS), k=rng.randint(0, 2))

    labels = [
        {"Name": l, "Confidence": rng.uniform(50, 95)}
        for l in detected_damage + detected_acc
    ]
    return {"Labels": labels, "damage_score": damage_score}


async def grade_from_images(image_data_list: list) -> dict:
    """
    Grade from list of raw image bytes.
    Returns full grading result.
    """
    all_damage_scores, accessories_found = [], []

    for img_bytes in image_data_list[:5]:
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
    }
