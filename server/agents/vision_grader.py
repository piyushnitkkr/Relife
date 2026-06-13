"""
Vision Grader — Uses Google Gemini Flash for AI-powered product condition grading.
Falls back to simulation if API key not configured.
Free Tier: 20 requests/day (Gemini 2.5 Flash).
"""
import base64
import json
import hashlib
import random
from config import settings

try:
    import google.generativeai as genai
    _genai_available = True
except ImportError:
    _genai_available = False

ACCESSORY_LABELS = {
    "Cable", "Charger", "Box", "Manual", "Adapter", "Remote",
    "Headphones", "Case", "Cover", "Bag",
}

GRADE_THRESHOLDS = [
    (0,  10,  "A", "Like New",       4, "Resell as Certified Refurbished"),
    (10, 30,  "B", "Minor Wear",     3, "Light Refurbishment"),
    (30, 60,  "C", "Refurbishable",  2, "Send for Repair"),
    (60, 100, "D", "Recycle",        1, "Recycle"),
]

# Initialize Gemini
_model = None
if _genai_available and settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
    except Exception:
        _model = None

GRADING_PROMPT = """You are a product condition grading AI for a refurbished marketplace.

Analyze this product image and provide a condition assessment. Return ONLY valid JSON (no markdown, no backticks):

{
  "damage_score": <number 0-100, where 0=perfect new condition, 100=completely broken>,
  "grade": "<A/B/C/D>",
  "condition_notes": "<brief description of visible condition>",
  "detected_damage": ["<list of damage types seen: scratch, dent, crack, stain, wear, etc>"],
  "accessories_visible": ["<list of accessories seen: box, cable, charger, manual, etc>"],
  "confidence": <number 0-100>
}

Grading scale:
- A (0-10% damage): Like New, no visible wear, possibly still sealed/boxed
- B (10-30% damage): Minor wear, light scratches, fully functional
- C (30-60% damage): Visible damage, scratches/dents, needs refurbishment
- D (60-100% damage): Heavy damage, broken parts, suitable for recycling

Be realistic and critical. Most used products are B or C grade."""


async def _grade_with_gemini(image_bytes: bytes) -> dict:
    """Send image to Gemini Flash for condition analysis."""
    image_data = {
        "mime_type": "image/jpeg",
        "data": base64.b64encode(image_bytes).decode("utf-8"),
    }

    response = _model.generate_content(
        [GRADING_PROMPT, image_data],
        generation_config=genai.GenerationConfig(
            temperature=0.2,
            max_output_tokens=500,
        ),
    )

    text = response.text.strip()
    # Clean up response — remove markdown code blocks if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    result = json.loads(text)
    return {
        "damage_score": min(100, max(0, result.get("damage_score", 20))),
        "accessories": result.get("accessories_visible", []),
        "condition_notes": result.get("condition_notes", ""),
        "detected_damage": result.get("detected_damage", []),
        "confidence": result.get("confidence", 80),
    }


def _simulate_analysis(image_bytes: bytes) -> dict:
    """Fallback simulation when Gemini unavailable."""
    digest = hashlib.md5(image_bytes).hexdigest()
    seed = int(digest[:8], 16)
    rng = random.Random(seed)

    roll = rng.random()
    if roll < 0.25:
        damage_score = rng.uniform(0, 8)
    elif roll < 0.50:
        damage_score = rng.uniform(12, 28)
    elif roll < 0.75:
        damage_score = rng.uniform(32, 55)
    else:
        damage_score = rng.uniform(62, 85)

    accessories = rng.sample(list(ACCESSORY_LABELS), k=rng.randint(0, 3))
    return {
        "damage_score": damage_score,
        "accessories": accessories,
        "condition_notes": "Simulated grading",
        "detected_damage": [],
        "confidence": 75,
    }


async def grade_from_images(image_data_list: list) -> dict:
    """
    Grade product condition from images.
    Uses Gemini Flash when API key configured, simulation otherwise.
    """
    all_damage_scores = []
    all_accessories = []
    all_notes = []
    all_damage_types = []
    use_gemini = _model is not None

    for img_bytes in image_data_list[:3]:  # Max 3 images to conserve quota
        if use_gemini:
            try:
                result = await _grade_with_gemini(img_bytes)
            except Exception as e:
                print(f"Gemini grading failed: {e}")
                result = _simulate_analysis(img_bytes)
        else:
            result = _simulate_analysis(img_bytes)

        all_damage_scores.append(result["damage_score"])
        all_accessories.extend(result.get("accessories", []))
        if result.get("condition_notes"):
            all_notes.append(result["condition_notes"])
        all_damage_types.extend(result.get("detected_damage", []))

    avg_damage = sum(all_damage_scores) / len(all_damage_scores) if all_damage_scores else 5.0

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
        "accessories_detected": list(set(all_accessories)),
        "recommendation":      recommendation,
        "images_analyzed":     len(image_data_list),
        "condition_notes":     "; ".join(all_notes) if all_notes else "",
        "damage_types":        list(set(all_damage_types)),
        "engine":              "gemini-flash" if use_gemini else "simulated",
    }
