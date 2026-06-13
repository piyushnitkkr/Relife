# ♻️ ReLife AI — Intelligent Second-Life Commerce Platform
### Hackathon Full Implementation Blueprint · MERN + FastAPI + AWS Free Tier

---

## 🧭 Problem & Solution

**The Problem:** Millions of returned, unused, or discarded products create enormous economic and environmental waste. Customers don't trust refurbished items. Returns are expensive for everyone.

**ReLife AI** turns every returned or idle product into an asset by building 7 intelligent systems directly inside the shopping experience:

| # | Feature | Core Benefit |
|---|---------|-------------|
| 1 | AI Product Lifecycle Engine | Decides resell / refurbish / donate / recycle automatically |
| 2 | Computer Vision Quality Grading | Grades condition from photos without manual inspection |
| 3 | Personalized Refurbished Recommendations | Builds trust with a transparent Health Score |
| 4 | Green Credits System | Rewards sustainable customer behaviour |
| 5 | P2P Marketplace | Connects real owners with buyers inside Amazon |
| 6 | Predictive Return Prevention | Warns before purchase, not after |
| 7 | Sustainability Dashboard | Shows personal environmental impact |

---

## 🏗️ Full System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          REACT FRONTEND (AWS Amplify Free)                   │
│  Cart │ Product Page │ Vision Upload │ P2P Market │ Dashboard │ Credits Panel │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │ HTTPS / WebSocket
                         ┌──────────▼──────────┐
                         │  AWS API Gateway    │  ← Free Tier: 1M calls/mo
                         │  (REST + WebSocket) │
                         └──────┬──────────────┘
                                │
          ┌─────────────────────┼──────────────────────┐
          │                     │                      │
┌─────────▼──────┐   ┌──────────▼────────┐   ┌────────▼────────┐
│  FastAPI App   │   │  AWS Lambda        │   │  AWS Lambda     │
│  (EC2 t2.micro)│   │  Vision Grader     │   │  Lifecycle      │
│  Free Tier     │   │  (Free 1M req/mo)  │   │  Classifier     │
└────────┬───────┘   └──────────┬─────────┘   └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
        ┌───────────────────────┼──────────────────────────┐
        │                       │                          │
┌───────▼──────┐    ┌───────────▼────────┐    ┌───────────▼──────┐
│  MongoDB     │    │  AWS S3             │    │  AWS DynamoDB    │
│  Atlas Free  │    │  (5 GB Free)        │    │  (25 GB Free)    │
│  512 MB      │    │  Images / Videos    │    │  Lifecycle data  │
└──────────────┘    └────────────────────┘    └──────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────┐
│              AWS Free Services Used                               │
│  Rekognition (5K images/mo) │ SES (62K emails/mo)                │
│  CloudWatch (10 metrics)    │ Cognito (50K MAU)                  │
│  SNS (1M notifs/mo)         │ SQS (1M requests/mo)               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
relife-ai/
├── client/                                  # React 18 + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── Cart/
│   │   │   │   ├── CartPage.jsx
│   │   │   │   ├── ReturnRiskBanner.jsx      # Feature 6
│   │   │   │   └── SecondhandPrompt.jsx      # Feature 5 CTA
│   │   │   ├── Lifecycle/
│   │   │   │   └── LifecycleDecision.jsx     # Feature 1
│   │   │   ├── Vision/
│   │   │   │   ├── ImageUploader.jsx         # Feature 2
│   │   │   │   └── GradeResult.jsx
│   │   │   ├── Recommendations/
│   │   │   │   ├── RefurbishedCard.jsx       # Feature 3
│   │   │   │   └── HealthScore.jsx
│   │   │   ├── Credits/
│   │   │   │   └── CreditsPanel.jsx          # Feature 4
│   │   │   ├── P2P/
│   │   │   │   ├── P2PRequestModal.jsx       # Feature 5
│   │   │   │   ├── SellerMatchCard.jsx
│   │   │   │   └── P2PChat.jsx
│   │   │   └── Dashboard/
│   │   │       └── SustainabilityDashboard.jsx  # Feature 7
│   │   ├── hooks/
│   │   │   ├── useCartAnalysis.js
│   │   │   ├── useVisionGrade.js
│   │   │   └── useP2PMatch.js
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── websocket.js
│   │   └── store/
│   │       ├── cartSlice.js
│   │       └── userSlice.js
│
├── server/                                  # FastAPI (Python 3.11)
│   ├── main.py
│   ├── routers/
│   │   ├── lifecycle.py                     # Feature 1
│   │   ├── vision.py                        # Feature 2
│   │   ├── recommendations.py               # Feature 3
│   │   ├── credits.py                       # Feature 4
│   │   ├── p2p.py                           # Feature 5
│   │   ├── cart.py                          # Feature 6
│   │   └── dashboard.py                     # Feature 7
│   ├── agents/
│   │   ├── lifecycle_classifier.py          # XGBoost model
│   │   ├── vision_grader.py                 # Rekognition + EfficientNet
│   │   ├── return_predictor.py              # Return probability model
│   │   ├── recommendation_engine.py         # Collaborative filtering
│   │   └── p2p_ranker.py                    # Match ranking
│   ├── models/
│   │   ├── product.py
│   │   ├── user.py
│   │   ├── p2p_listing.py
│   │   └── lifecycle_event.py
│   ├── ml/
│   │   ├── train_lifecycle.py               # XGBoost training script
│   │   ├── train_return_predictor.py
│   │   └── models/                          # Saved .pkl model files
│   ├── db/
│   │   ├── mongo.py
│   │   └── dynamo.py
│   └── requirements.txt
│
├── lambdas/                                 # AWS Lambda functions
│   ├── vision_lambda/
│   │   └── handler.py                       # Rekognition grader
│   └── lifecycle_lambda/
│       └── handler.py                       # XGBoost inference
│
├── infra/
│   ├── template.yaml                        # AWS SAM / CloudFormation
│   └── amplify.yml                          # Amplify build config
│
└── docker-compose.yml                       # Local dev
```

---

## ☁️ AWS Free Tier — Complete Service Map

| AWS Service | Free Tier Limit | Used For |
|-------------|----------------|----------|
| **EC2 t2.micro** | 750 hrs/mo (12 months) | FastAPI app server |
| **AWS Amplify** | 5 GB storage, 15 GB serving/mo | React frontend hosting |
| **API Gateway** | 1M API calls/mo | REST + WebSocket routing |
| **Lambda** | 1M requests/mo, 400K GB-sec | Vision grader, lifecycle classifier |
| **S3** | 5 GB, 20K GET, 2K PUT | Product images & videos |
| **DynamoDB** | 25 GB, 25 RCU/WCU | Lifecycle decisions, sessions |
| **Amazon Rekognition** | 5,000 images/mo | Computer vision grading |
| **Cognito** | 50,000 MAU | User auth |
| **SNS** | 1M notifications/mo | Push notifications to sellers |
| **SQS** | 1M requests/mo | Async job queue |
| **SES** | 62,000 emails/mo | Email notifications |
| **CloudWatch** | 10 custom metrics, 5 GB logs | Monitoring |
| **MongoDB Atlas** | 512 MB (M0 free cluster) | Orders, users, P2P data |

> **Cost at hackathon scale: $0.00/month** — all within free tier limits.

---

## ⚙️ Tech Stack

| Layer | Technology | Why Free |
|-------|-----------|----------|
| Frontend | React 18 + Vite + Tailwind | Open source |
| Hosting | AWS Amplify Free | Free tier |
| State | Redux Toolkit | Open source |
| Auth | AWS Cognito Free Tier | 50K MAU free |
| Backend | FastAPI on EC2 t2.micro | 750 hrs/mo free |
| Serverless | AWS Lambda | 1M req/mo free |
| Vision AI | AWS Rekognition + OpenCV | 5K images/mo free |
| ML Models | Scikit-learn XGBoost | Open source, runs on EC2 |
| Database | MongoDB Atlas M0 | Free 512MB cluster |
| Key-Value | AWS DynamoDB | 25 GB free |
| File Store | AWS S3 | 5 GB free |
| Queue | AWS SQS | 1M req/mo free |
| Notifications | AWS SNS | 1M/mo free |
| Real-time | API Gateway WebSocket | 1M/mo free |
| LLM | Claude API (Anthropic) / Ollama local | Free trial / local |
| Recommender | Surprise library (SVD) | Open source |

---

## 🔧 Feature 1 — AI Product Lifecycle Engine

### Decision Logic

```
Returned Product
      ↓
   Inputs: category, return_reason, product_age_days,
           return_frequency, repair_cost_estimate,
           vision_grade, seller_reputation
      ↓
  XGBoost Classifier
      ↓
┌────────────┬────────────────────────────────┐
│ Condition  │ Action                         │
├────────────┼────────────────────────────────┤
│ Like New   │ → Certified Refurbished Resell │
│ Minor Dmg  │ → Refurbish + Resell           │
│ Functional │ → Exchange Marketplace         │
│ Low Demand │ → Donate via NGO API           │
│ Broken     │ → Recycle Partner              │
└────────────┴────────────────────────────────┘
```

### `server/agents/lifecycle_classifier.py`

```python
import pickle
import numpy as np
from pathlib import Path
import boto3
import json

# Load trained XGBoost model (stored locally on EC2 / Lambda /tmp)
MODEL_PATH = Path(__file__).parent.parent / "ml" / "models" / "lifecycle_xgb.pkl"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

LABEL_MAP = {
    0: {"action": "resell_certified",    "label": "Certified Refurbished"},
    1: {"action": "refurbish",           "label": "Send for Refurbishment"},
    2: {"action": "exchange_marketplace","label": "Exchange Marketplace"},
    3: {"action": "donate",              "label": "Donate to NGO"},
    4: {"action": "recycle",             "label": "Recycle"},
}

CATEGORY_ENCODING = {
    "electronics": 0, "clothing": 1, "baby_products": 2,
    "furniture": 3, "sports": 4, "books": 5, "other": 6,
}

RETURN_REASON_ENCODING = {
    "defective": 0, "wrong_item": 1, "size_issue": 2,
    "changed_mind": 3, "better_price": 4, "not_as_described": 5,
}

def build_feature_vector(data: dict) -> np.ndarray:
    return np.array([[
        CATEGORY_ENCODING.get(data.get("category", "other"), 6),
        RETURN_REASON_ENCODING.get(data.get("return_reason", "changed_mind"), 3),
        min(data.get("product_age_days", 0), 1825) / 1825,   # normalize 0-5 years
        min(data.get("return_frequency", 0), 10) / 10,
        min(data.get("repair_cost_estimate", 0), 5000) / 5000,
        data.get("vision_grade_numeric", 2) / 4,              # 0-4 scale
        min(data.get("seller_reputation", 3.0), 5.0) / 5.0,
        1 if data.get("accessories_present", False) else 0,
        min(data.get("days_since_purchase", 0), 365) / 365,
    ]])

def classify_lifecycle(data: dict) -> dict:
    features = build_feature_vector(data)
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = round(float(probabilities[prediction]) * 100, 1)
    result = LABEL_MAP[prediction]
    return {
        "action":      result["action"],
        "label":       result["label"],
        "confidence":  confidence,
        "all_scores":  {LABEL_MAP[i]["label"]: round(float(p)*100,1)
                        for i, p in enumerate(probabilities)},
        "green_credits_awarded": _credits_for_action(result["action"]),
    }

def _credits_for_action(action: str) -> int:
    return {"resell_certified": 50, "refurbish": 35,
            "exchange_marketplace": 30, "donate": 60, "recycle": 25}.get(action, 0)
```

### Training Script — `server/ml/train_lifecycle.py`

```python
"""
Run once to train and save the model.
Uses synthetic + historical order data from MongoDB.
Run: python -m ml.train_lifecycle
"""
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle, numpy as np
from db.mongo import db

def load_training_data():
    records = list(db.lifecycle_events.find({"label": {"$exists": True}}))
    X, y = [], []
    for r in records:
        from agents.lifecycle_classifier import build_feature_vector, LABEL_MAP
        inv_map = {v["action"]: k for k, v in LABEL_MAP.items()}
        if r.get("label") in inv_map:
            X.append(build_feature_vector(r)[0])
            y.append(inv_map[r["label"]])
    return np.array(X), np.array(y)

def train():
    X, y = load_training_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                          use_label_encoder=False, eval_metric="mlogloss")
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    print(classification_report(y_test, model.predict(X_test)))
    with open("ml/models/lifecycle_xgb.pkl", "wb") as f:
        pickle.dump(model, f)
    print("✅ Model saved to ml/models/lifecycle_xgb.pkl")

if __name__ == "__main__":
    train()
```

### Router — `server/routers/lifecycle.py`

```python
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from agents.lifecycle_classifier import classify_lifecycle
from agents.vision_grader import grade_from_images
from db.mongo import db
from utils.auth import get_current_user
import boto3, uuid
from datetime import datetime

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])
s3 = boto3.client("s3", region_name="us-east-1")
BUCKET = "relife-ai-assets"   # your free S3 bucket

class LifecycleInput(BaseModel):
    product_id: str
    category: str
    return_reason: str
    product_age_days: int
    return_frequency: int = 0
    repair_cost_estimate: float = 0.0
    seller_reputation: float = 4.0
    accessories_present: bool = True

@router.post("/classify")
async def classify_product(data: LifecycleInput, user=Depends(get_current_user)):
    result = classify_lifecycle(data.dict())
    db.lifecycle_events.insert_one({
        "product_id": data.product_id,
        "user_id": user["user_id"],
        "input": data.dict(),
        "result": result,
        "created_at": datetime.utcnow(),
    })
    return result

@router.post("/classify-with-images")
async def classify_with_images(
    product_id: str = Form(...),
    category: str = Form(...),
    return_reason: str = Form(...),
    product_age_days: int = Form(...),
    images: list[UploadFile] = File(...),
    user=Depends(get_current_user)
):
    # Upload images to S3 (free 5 GB)
    image_urls = []
    for img in images:
        key = f"returns/{product_id}/{uuid.uuid4()}-{img.filename}"
        content = await img.read()
        s3.put_object(Bucket=BUCKET, Key=key, Body=content,
                      ContentType=img.content_type)
        image_urls.append(f"https://{BUCKET}.s3.amazonaws.com/{key}")

    # Grade via Rekognition (free 5K images/mo)
    vision_result = await grade_from_images(image_urls)

    payload = {
        "product_id": product_id, "category": category,
        "return_reason": return_reason, "product_age_days": product_age_days,
        "vision_grade_numeric": vision_result["grade_numeric"],
    }
    lifecycle_result = classify_lifecycle(payload)

    return {
        "vision_grade": vision_result,
        "lifecycle_decision": lifecycle_result,
        "image_urls": image_urls,
    }
```

---

## 👁️ Feature 2 — Computer Vision Quality Grading

### Grade Scale

| Grade | Label | Rekognition Signal |
|-------|-------|-------------------|
| A | Like New | No damage labels detected |
| B | Minor Wear | Scratch/scuff < 10% confidence |
| C | Refurbishable | Damage labels 10–40% |
| D | Recycle | Damage > 40% or broken labels |

### `server/agents/vision_grader.py`

```python
import boto3
import urllib.request
from PIL import Image
import io

rekognition = boto3.client("rekognition", region_name="us-east-1")

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

async def grade_from_images(image_urls: list[str]) -> dict:
    all_damage_scores, accessories_found = [], []

    for url in image_urls[:5]:   # max 5 images to stay in free tier
        with urllib.request.urlopen(url) as response:
            image_bytes = response.read()

        # AWS Rekognition label detection (free: 5,000 images/mo)
        response = rekognition.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=30,
            MinConfidence=50
        )

        labels = response.get("Labels", [])
        label_names = {l["Name"] for l in labels}
        damage_labels = label_names & DAMAGE_LABELS
        acc_labels = label_names & ACCESSORY_LABELS

        # Aggregate damage confidence
        damage_conf = max(
            (l["Confidence"] for l in labels if l["Name"] in DAMAGE_LABELS),
            default=0
        )
        all_damage_scores.append(damage_conf)

        if acc_labels:
            accessories_found.extend(list(acc_labels))

    avg_damage = sum(all_damage_scores) / len(all_damage_scores) if all_damage_scores else 0

    # Determine grade
    grade_letter, grade_label, grade_numeric, recommendation = "A", "Like New", 4, "Resell"
    for lo, hi, letter, label, numeric, rec in GRADE_THRESHOLDS:
        if lo <= avg_damage < hi:
            grade_letter, grade_label, grade_numeric, recommendation = letter, label, numeric, rec
            break

    return {
        "grade":            grade_letter,
        "grade_label":      grade_label,
        "grade_numeric":    grade_numeric,
        "confidence":       round(100 - avg_damage, 1),
        "damage_score_pct": round(avg_damage, 1),
        "accessories_detected": list(set(accessories_found)),
        "recommendation":   recommendation,
        "images_analyzed":  len(image_urls),
    }
```

### Frontend — `client/src/components/Vision/ImageUploader.jsx`

```jsx
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { gradeImages } from "../../services/api";

const GRADE_COLORS = {
  A: "bg-green-100 border-green-500 text-green-800",
  B: "bg-blue-100 border-blue-500 text-blue-800",
  C: "bg-yellow-100 border-yellow-500 text-yellow-800",
  D: "bg-red-100 border-red-500 text-red-800",
};

export default function ImageUploader({ productId, category, onGrade }) {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const onDrop = useCallback((accepted) => {
    setFiles(accepted);
    setPreviews(accepted.map((f) => URL.createObjectURL(f)));
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "image/*": [] }, maxFiles: 5,
  });

  const handleGrade = async () => {
    if (files.length === 0) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("product_id", productId);
      formData.append("category", category);
      formData.append("return_reason", "changed_mind");
      formData.append("product_age_days", "365");
      files.forEach((f) => formData.append("images", f));
      const data = await gradeImages(formData);
      setResult(data);
      onGrade?.(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition ${isDragActive ? "border-green-500 bg-green-50" : "border-gray-300 hover:border-green-400"}`}
      >
        <input {...getInputProps()} />
        <div className="text-4xl mb-2">📸</div>
        <p className="text-gray-600 font-medium">Drop product photos here</p>
        <p className="text-sm text-gray-400">Up to 5 images · PNG, JPG, WEBP</p>
      </div>

      {previews.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {previews.map((src, i) => (
            <img key={i} src={src} alt=""
                 className="w-20 h-20 object-cover rounded-lg border" />
          ))}
        </div>
      )}

      <button
        onClick={handleGrade}
        disabled={loading || files.length === 0}
        className="w-full bg-indigo-600 text-white py-3 rounded-xl
                     font-bold hover:bg-indigo-700 transition disabled:opacity-40"
      >
        {loading ? "Analysing with AI…" : "🔍 Grade My Product"}
      </button>

      {result && (
        <div className={`border-2 rounded-xl p-5 ${GRADE_COLORS[result.vision_grade.grade]}`}>
          <div className="flex justify-between items-center mb-3">
            <span className="text-3xl font-black">
              Grade {result.vision_grade.grade}
            </span>
            <span className="text-lg font-semibold">
              {result.vision_grade.grade_label}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="opacity-60">Confidence</span>
              <p className="font-bold">{result.vision_grade.confidence}%</p>
            </div>
            <div>
              <span className="opacity-60">Damage Score</span>
              <p className="font-bold">{result.vision_grade.damage_score_pct}%</p>
            </div>
            <div>
              <span className="opacity-60">Accessories</span>
              <p className="font-bold">
                {result.vision_grade.accessories_detected.join(", ") || "None detected"}
              </p>
            </div>
            <div>
              <span className="opacity-60">Recommendation</span>
              <p className="font-bold">{result.vision_grade.recommendation}</p>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-current border-opacity-20">
            <p className="font-semibold">
              Lifecycle Decision: {result.lifecycle_decision.label}
            </p>
            <p className="text-xs opacity-70 mt-1">
              +{result.lifecycle_decision.green_credits_awarded} Green Credits awarded
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 🎯 Feature 3 — Personalized Refurbished Recommendations

### Health Score Formula

```
Product Health Score (0–100) =
  (Vision Grade Score × 0.35)     # physical condition
+ (Repair History Score × 0.20)   # how many repairs
+ (Warranty Remaining × 0.20)     # months left / total
+ (Seller Rating × 0.15)          # seller reputation
+ (Battery/Component Health × 0.10) # for electronics
```

### `server/agents/recommendation_engine.py`

```python
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate
import pandas as pd
import pickle
from db.mongo import db
from datetime import datetime

def calculate_health_score(product: dict) -> dict:
    """Calculate transparent trust score for refurbished products."""
    grade_map = {"A": 100, "B": 75, "C": 50, "D": 20}
    grade_score = grade_map.get(product.get("vision_grade", "B"), 75)

    repairs = product.get("repair_count", 0)
    repair_score = max(0, 100 - (repairs * 15))

    warranty_months = product.get("warranty_months_remaining", 0)
    warranty_total = product.get("warranty_months_total", 12)
    warranty_score = (warranty_months / max(warranty_total, 1)) * 100

    seller_rating = product.get("seller_rating", 4.0)
    seller_score = (seller_rating / 5.0) * 100

    battery = product.get("battery_health_pct", 100)

    health_score = (
        grade_score   * 0.35 +
        repair_score  * 0.20 +
        warranty_score * 0.20 +
        seller_score  * 0.15 +
        battery       * 0.10
    )

    return {
        "health_score":         round(health_score, 1),
        "breakdown": {
            "condition":        round(grade_score * 0.35, 1),
            "repair_history":   round(repair_score * 0.20, 1),
            "warranty":         round(warranty_score * 0.20, 1),
            "seller_trust":     round(seller_score * 0.15, 1),
            "component_health": round(battery * 0.10, 1),
        },
        "trust_badge": (
            "🏆 Highly Trusted" if health_score >= 85 else
            "✅ Verified Good"   if health_score >= 70 else
            "⚠️ Use with Caution"
        ),
    }

def get_collaborative_recommendations(user_id: str, n: int = 6) -> list:
    """SVD collaborative filtering using Surprise library (open source)."""
    # Build ratings matrix from purchase + rating history
    ratings = list(db.product_ratings.find(
        {}, {"user_id": 1, "product_id": 1, "rating": 1, "_id": 0}
    ).limit(10000))

    if len(ratings) < 50:
        # Fallback: return top-rated refurbished products
        return list(db.refurbished_products.find(
            {"health_score": {"$gte": 70}}
        ).sort("health_score", -1).limit(n))

    df = pd.DataFrame(ratings)
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["user_id", "product_id", "rating"]], reader)

    try:
        with open("ml/models/svd_recommender.pkl", "rb") as f:
            algo = pickle.load(f)
    except FileNotFoundError:
        algo = SVD(n_factors=50, n_epochs=20, lr_all=0.005, reg_all=0.02)
        trainset = data.build_full_trainset()
        algo.fit(trainset)
        with open("ml/models/svd_recommender.pkl", "wb") as f:
            pickle.dump(algo, f)

    all_products = db.refurbished_products.distinct("product_id")
    bought = {r["product_id"] for r in db.orders.find({"user_id": user_id}, {"product_id": 1})}
    candidates = [p for p in all_products if p not in bought]

    predictions = [(pid, algo.predict(user_id, pid).est) for pid in candidates]
    top_pids = [p for p, _ in sorted(predictions, key=lambda x: -x[1])[:n]]

    products = list(db.refurbished_products.find({"product_id": {"$in": top_pids}}))
    for p in products:
        health = calculate_health_score(p)
        p["health_score"] = health["health_score"]
        p["trust_badge"]  = health["trust_badge"]
        p["breakdown"]    = health["breakdown"]
    return products
```

### Frontend — `client/src/components/Recommendations/RefurbishedCard.jsx`

```jsx
export default function RefurbishedCard({ product }) {
  const score = product.health_score;
  const scoreColor =
    score >= 85 ? "text-green-600" : score >= 70 ? "text-blue-600" : "text-yellow-600";

  return (
    <div className="border rounded-2xl overflow-hidden shadow-sm
                     hover:shadow-md transition bg-white">
      <div className="relative">
        <img src={product.image} alt={product.name}
             className="w-full h-44 object-cover" />
        <span className="absolute top-2 right-2 bg-green-600 text-white
                           text-xs font-bold px-2 py-1 rounded-full">
          ♻️ Refurbished
        </span>
        <span className="absolute top-2 left-2 bg-white text-xs font-bold
                           px-2 py-1 rounded-full shadow">
          {product.trust_badge}
        </span>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-sm leading-tight mb-1">{product.name}</h3>
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-2xl font-black ${scoreColor}`}>{score}</span>
          <span className="text-xs text-gray-400">/ 100 Health Score</span>
        </div>

        {/* Score breakdown bar */}
        <div className="space-y-1 mb-3">
          {Object.entries(product.breakdown).map(([key, val]) => (
            <div key={key} className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-28 capitalize">
                {key.replace("_", " ")}
              </span>
              <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                <div
                  className="bg-green-500 h-1.5 rounded-full transition-all"
                  style={{ width: `${Math.min(val * 3, 100)}%` }}
                />
              </div>
              <span className="text-xs text-gray-500 w-8 text-right">
                {val}
              </span>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between">
          <div>
            <span className="text-lg font-bold text-green-700">
              ₹{product.refurb_price?.toLocaleString()}
            </span>
            <span className="text-xs text-gray-400 ml-1 line-through">
              ₹{product.original_price?.toLocaleString()}
            </span>
          </div>
          <button className="bg-[#FF9900] text-white text-xs font-bold
                               px-3 py-1.5 rounded-lg hover:bg-orange-500 transition">
            Add to Cart
          </button>
        </div>
        {product.warranty_months_remaining > 0 && (
          <p className="text-xs text-blue-600 mt-2">
            🛡️ {product.warranty_months_remaining} months warranty remaining
          </p>
        )}
      </div>
    </div>
  );
}
```

---

## 🌿 Feature 4 — Green Credits System

### Credit Rules

```python
# server/routers/credits.py

from fastapi import APIRouter, Depends
from db.mongo import db
from db.dynamo import dynamo_table
from utils.auth import get_current_user
import boto3
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

CREDIT_TO_INR = 0.5   # 1 Green Credit = ₹0.50 in coupon value

@router.post("/award/{event}")
async def award_credits(event: str, user=Depends(get_current_user)):
    points = CREDIT_RULES.get(event)
    if points is None or points < 0:
        return {"error": "Unknown or non-earning event"}

    # Update in MongoDB (primary)
    db.users.update_one(
        {"_id": user["user_id"]},
        {"$inc": {"green_credits": points},
         "$push": {"credit_history": {
             "event": event, "points": points,
             "timestamp": datetime.utcnow()
         }}}
    )
    # Sync to DynamoDB for fast reads (free 25 GB)
    dynamo_table.update_item(
        Key={"user_id": user["user_id"]},
        UpdateExpression="ADD green_credits :p",
        ExpressionAttributeValues={":p": points}
    )
    return {
        "awarded":     points,
        "event":       event,
        "inr_value":   f"₹{points * CREDIT_TO_INR:.0f}",
        "message":     f"🌿 +{points} Green Credits earned!",
    }

@router.post("/redeem/{event}")
async def redeem_credits(event: str, user=Depends(get_current_user)):
    cost = abs(CREDIT_RULES.get(event, 0))
    if cost == 0:
        return {"error": "Unknown redemption event"}
    user_doc = db.users.find_one({"_id": user["user_id"]}, {"green_credits": 1})
    balance = user_doc.get("green_credits", 0)
    if balance < cost:
        return {"error": f"Insufficient credits. Need {cost}, have {balance}"}
    db.users.update_one({"_id": user["user_id"]}, {"$inc": {"green_credits": -cost}})
    return {"redeemed": cost, "new_balance": balance - cost,
            "coupon_code": f"RELIFE-{user['user_id'][:6].upper()}-{cost}"}

@router.get("/balance")
async def get_balance(user=Depends(get_current_user)):
    result = dynamo_table.get_item(Key={"user_id": user["user_id"]})
    balance = result.get("Item", {}).get("green_credits", 0)
    return {
        "balance":   int(balance),
        "inr_value": f"₹{int(balance) * CREDIT_TO_INR:.0f}",
        "tier": (
            "🌳 Eco Champion" if balance >= 500 else
            "🌿 Green Member" if balance >= 200 else
            "🌱 Getting Started"
        )
    }
```

---

## 🔄 Feature 5 — Amazon P2P Marketplace

### `server/routers/p2p.py`

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
from db.mongo import db
from utils.timeline import get_lifecycle_window
from utils.auth import get_current_user
from agents.p2p_ranker import rank_sellers
import boto3, uuid

router = APIRouter(prefix="/p2p", tags=["p2p"])
sns = boto3.client("sns", region_name="us-east-1")   # Free: 1M notifs/mo

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
    product_id: str
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
    user=Depends(get_current_user)
):
    request_id = str(uuid.uuid4())
    window = CATEGORY_LIFECYCLE.get(req.category, CATEGORY_LIFECYCLE["default"])
    now = datetime.utcnow()
    after  = now - timedelta(days=window["max_months"] * 30)
    before = now - timedelta(days=window["min_months"] * 30)

    db.p2p_requests.insert_one({
        "_id": request_id, "buyer_id": user["user_id"],
        "category": req.category, "max_budget": req.max_budget,
        "condition": req.condition, "status": "open", "created_at": now,
    })

    # Smart query: users who bought this category in the lifecycle window
    pipeline = [
        {"$match": {
            "product_category": req.category,
            "status": {"$in": ["delivered", "completed"]},
            "purchase_date": {"$gte": after, "$lte": before},
            "user_id": {"$ne": user["user_id"]},
            "p2p_listed": {"$ne": True},
        }},
        {"$lookup": {
            "from": "users", "localField": "user_id",
            "foreignField": "_id", "as": "seller_info"
        }},
        {"$unwind": "$seller_info"},
        {"$project": {
            "user_id": 1, "product_name": 1, "purchase_date": 1,
            "seller_info.name": 1, "seller_info.rating": 1,
            "seller_info.sns_endpoint_arn": 1,
        }},
        {"$limit": 50}
    ]
    sellers = list(db.orders.aggregate(pipeline))
    ranked  = await rank_sellers(sellers, req.dict(), user)

    bg.add_task(_notify_sellers_sns, ranked[:10], request_id, req)
    return {
        "request_id":       request_id,
        "potential_matches": len(sellers),
        "top_preview":      ranked[:3],
        "message": f"Notifying {min(len(sellers), 10)} potential sellers via Amazon SNS!"
    }

@router.post("/seller/optin")
async def seller_opt_in(optin: SellerOptIn, user=Depends(get_current_user)):
    req = db.p2p_requests.find_one({"_id": optin.request_id})
    if not req:
        return {"error": "Request not found"}
    listing_id = str(uuid.uuid4())
    db.p2p_listings.insert_one({
        "_id": listing_id,
        "request_id":  optin.request_id,
        "seller_id":   user["user_id"],
        "buyer_id":    req["buyer_id"],
        "price":       optin.listing_price,
        "condition":   optin.condition,
        "description": optin.description,
        "status":      "pending_acceptance",
        "created_at":  datetime.utcnow(),
    })
    # Notify buyer via SNS
    buyer = db.users.find_one({"_id": req["buyer_id"]}, {"sns_endpoint_arn": 1})
    if buyer and buyer.get("sns_endpoint_arn"):
        sns.publish(
            TargetArn=buyer["sns_endpoint_arn"],
            Message=f"A seller matched your request! Check ReLife AI.",
            Subject="ReLife AI — Seller Found 🎉"
        )
    return {"listing_id": listing_id, "status": "pending_acceptance"}

async def _notify_sellers_sns(sellers, request_id, req):
    for s in sellers:
        arn = s.get("seller_info", {}).get("sns_endpoint_arn")
        if arn:
            sns.publish(
                TargetArn=arn,
                Message=(
                    f"Someone wants to buy a used {req.category}! "
                    f"Budget: ₹{req.max_budget:,.0f}. "
                    f"Open ReLife AI to opt in."
                ),
                Subject="ReLife AI — Sell Your Unused Product 💚"
            )
        # Fallback: store in-app notification
        db.notifications.insert_one({
            "user_id": s["user_id"], "type": "p2p_sell_opportunity",
            "title": "Someone wants to buy your product!",
            "body": f"Budget: ₹{req.max_budget:,.0f} for {req.category}.",
            "request_id": request_id, "read": False,
            "created_at": datetime.utcnow(),
        })
```

---

## 🔮 Feature 6 — Predictive Return Prevention

### `server/agents/return_predictor.py`

```python
import pickle
import numpy as np
from db.mongo import db
from sklearn.ensemble import RandomForestClassifier
import json

def load_or_train_model():
    try:
        with open("ml/models/return_predictor.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        # Bootstrap with synthetic data if no training data yet
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        X = np.random.rand(500, 8)
        y = (X[:, 0] + X[:, 2] > 1.1).astype(int)
        model.fit(X, y)
        with open("ml/models/return_predictor.pkl", "wb") as f:
            pickle.dump(model, f)
        return model

model = load_or_train_model()

def predict_return_risk(user_id: str, product: dict) -> dict:
    # Fetch user signals from MongoDB
    user = db.users.find_one({"_id": user_id}) or {}
    orders = list(db.orders.find({"user_id": user_id}).limit(50))
    total  = max(len(orders), 1)
    returned = sum(1 for o in orders if o.get("status") == "returned")
    same_cat  = [o for o in orders if o.get("product_category") == product.get("category", "")]
    cat_returns = sum(1 for o in same_cat if o.get("status") == "returned")

    global_signals = db.return_signals.find_one(
        {"product_id": product.get("product_id", "")}) or {}

    features = np.array([[
        returned / total,                                      # personal return rate
        cat_returns / max(len(same_cat), 1),                   # category return rate
        min(global_signals.get("return_rate_pct", 15), 100) / 100,  # global product return rate
        1 if product.get("category") in ["clothing", "shoes", "fashion"] else 0,
        1 if product.get("size") else 0,                       # size-dependent item
        min(product.get("price", 0), 50000) / 50000,           # price normalised
        min(user.get("account_age_days", 0), 1825) / 1825,
        1 if user.get("prime_member") else 0,
    ]])

    prob = model.predict_proba(features)[0][1]
    risk_score = round(prob * 100)

    reasons, tips = [], []
    if returned / total > 0.3:
        reasons.append("you have a high personal return rate")
    if cat_returns / max(len(same_cat), 1) > 0.4:
        reasons.append(f"you've returned {product.get('category', 'similar')} items before")
    if global_signals.get("return_rate_pct", 0) > 35:
        reasons.append(f"this product has a {global_signals['return_rate_pct']:.0f}% global return rate")
        top = global_signals.get("top_reasons", [])
        if top:
            tips.append(f"Common reason: {top[0].replace('_', ' ')}")
    if product.get("category") in ["clothing", "shoes"]:
        tips.append("Check the size guide carefully before ordering")

    return {
        "risk_score":   risk_score,
        "risk_level":   "High" if risk_score >= 70 else "Medium" if risk_score >= 45 else "Low",
        "reason":       f"Our AI flagged this because {' and '.join(reasons)}." if reasons
                        else "Low return risk based on your profile.",
        "tip":          tips[0] if tips else "You're likely to enjoy this product!",
        "top_return_reasons": global_signals.get("top_reasons", [])[:3],
    }
```

### Router — `server/routers/cart.py`

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from agents.return_predictor import predict_return_risk
from utils.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])

class CartItem(BaseModel):
    product_id: str
    category: str
    color:  str | None = None
    size:   str | None = None
    price:  float | None = None

class CartAnalyzeRequest(BaseModel):
    items: list[CartItem]

@router.post("/analyze")
async def analyze_cart(req: CartAnalyzeRequest, user=Depends(get_current_user)):
    return {
        "analysis": [
            {
                "product_id":   item.product_id,
                "return_risk":  predict_return_risk(user["user_id"], item.dict()),
            }
            for item in req.items
        ]
    }
```

### Frontend — `client/src/components/Cart/ReturnRiskBanner.jsx`

```jsx
import { useEffect, useState } from "react";
import { analyzeCart } from "../../services/api";

const LEVEL_STYLE = {
  High:   "bg-red-50 border-red-400 text-red-900",
  Medium: "bg-yellow-50 border-yellow-400 text-yellow-900",
  Low:    "bg-green-50 border-green-400 text-green-900",
};

export default function ReturnRiskBanner({ cartItems }) {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!cartItems?.length) return;
    setLoading(true);
    analyzeCart(cartItems)
      .then((d) => setRisks(d.analysis.filter((r) => r.return_risk.risk_score >= 45)))
      .finally(() => setLoading(false));
  }, [cartItems]);

  if (loading) return <p className="text-sm text-gray-400 p-2">Checking return risk…</p>;
  if (!risks.length) return null;

  return (
    <div className="space-y-3 my-4">
      {risks.map((r) => {
        const risk = r.return_risk;
        return (
          <div key={r.product_id}
               className={`border-l-4 p-4 rounded-lg ${LEVEL_STYLE[risk.risk_level]}`}>
            <div className="flex justify-between items-center font-bold text-sm mb-1">
              <span>⚠️ {risk.risk_level} Return Risk</span>
              <span className="text-lg">{risk.risk_score}%</span>
            </div>
            <p className="text-sm">{risk.reason}</p>
            <p className="text-xs mt-1 opacity-75">💡 {risk.tip}</p>
            {risk.top_return_reasons.length > 0 && (
              <p className="text-xs mt-1 opacity-60">
                Top return reasons: {risk.top_return_reasons.map(r => r.replace(/_/g," ")).join(" · ")}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
```

---

## 📊 Feature 7 — Sustainability Dashboard

### `server/routers/dashboard.py`

```python
from fastapi import APIRouter, Depends
from db.mongo import db
from utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

CO2_PER_AVOIDED_RETURN_KG   = 2.5
CO2_PER_REFURBISHED_BUY_KG  = 4.0
CO2_PER_DONATED_ITEM_KG     = 1.8
CO2_PER_RECYCLED_ITEM_KG    = 1.2

@router.get("/sustainability")
async def get_sustainability_stats(user=Depends(get_current_user)):
    uid = user["user_id"]

    products_saved = db.lifecycle_events.count_documents({
        "user_id": uid,
        "result.action": {"$in": ["resell_certified","refurbish","donate","exchange_marketplace"]}
    })
    returns_avoided = db.cart_events.count_documents({
        "user_id": uid, "event": "return_avoided"
    })
    refurb_bought = db.orders.count_documents({
        "user_id": uid, "product_type": "refurbished"
    })
    items_donated = db.lifecycle_events.count_documents({
        "user_id": uid, "result.action": "donate"
    })
    items_recycled = db.lifecycle_events.count_documents({
        "user_id": uid, "result.action": "recycle"
    })
    p2p_completed = db.p2p_listings.count_documents({
        "$or": [{"seller_id": uid}, {"buyer_id": uid}],
        "status": "completed"
    })

    co2_saved = round(
        returns_avoided  * CO2_PER_AVOIDED_RETURN_KG +
        refurb_bought    * CO2_PER_REFURBISHED_BUY_KG +
        items_donated    * CO2_PER_DONATED_ITEM_KG +
        items_recycled   * CO2_PER_RECYCLED_ITEM_KG,
        1
    )

    user_doc = db.users.find_one({"_id": uid}, {"green_credits": 1})
    credits = user_doc.get("green_credits", 0)

    return {
        "products_saved":    products_saved,
        "co2_saved_kg":      co2_saved,
        "trees_equivalent":  round(co2_saved / 21, 2),
        "items_donated":     items_donated,
        "items_recycled":    items_recycled,
        "p2p_exchanges":     p2p_completed,
        "returns_avoided":   returns_avoided,
        "refurb_bought":     refurb_bought,
        "green_credits":     credits,
        "impact_level": (
            "🌍 Planet Hero"   if products_saved >= 20 else
            "🌳 Eco Champion"  if products_saved >= 10 else
            "🌿 Green Starter"
        )
    }
```

### Frontend — `client/src/components/Dashboard/SustainabilityDashboard.jsx`

```jsx
import { useEffect, useState } from "react";
import { getDashboard } from "../../services/api";

const StatCard = ({ icon, label, value, sub, color }) => (
  <div className={`rounded-2xl p-5 ${color} flex flex-col gap-1`}>
    <span className="text-3xl">{icon}</span>
    <span className="text-2xl font-black">{value}</span>
    <span className="font-semibold text-sm">{label}</span>
    {sub && <span className="text-xs opacity-70">{sub}</span>}
  </div>
);

export default function SustainabilityDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getDashboard().then(setStats);
  }, []);

  if (!stats) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin text-4xl">🌿</div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">

      {/* Hero banner */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-500
                       text-white rounded-3xl p-8 text-center">
        <div className="text-5xl mb-2">{stats.impact_level.split(" ")[0]}</div>
        <h1 className="text-2xl font-black mb-1">{stats.impact_level}</h1>
        <p className="opacity-80">Your sustainable shopping impact</p>
      </div>

      {/* Core stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon="📦" label="Products Saved"
          value={stats.products_saved}
          sub="from landfill"
          color="bg-green-50 text-green-800" />
        <StatCard icon="🌫️" label="CO₂ Saved"
          value={`${stats.co2_saved_kg} kg`}
          sub={`≈ ${stats.trees_equivalent} trees planted`}
          color="bg-blue-50 text-blue-800" />
        <StatCard icon="🤝" label="Items Donated"
          value={stats.items_donated}
          sub="to NGOs"
          color="bg-purple-50 text-purple-800" />
        <StatCard icon="🌿" label="Green Credits"
          value={stats.green_credits}
          sub={`≈ ₹${(stats.green_credits * 0.5).toFixed(0)} value`}
          color="bg-emerald-50 text-emerald-800" />
      </div>

      {/* Secondary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon="🔄" label="Returns Avoided"
          value={stats.returns_avoided} sub=""
          color="bg-orange-50 text-orange-800" />
        <StatCard icon="♻️" label="Recycled"
          value={stats.items_recycled} sub="items"
          color="bg-gray-50 text-gray-800" />
        <StatCard icon="🤜🤛" label="P2P Exchanges"
          value={stats.p2p_exchanges} sub="completed"
          color="bg-yellow-50 text-yellow-800" />
        <StatCard icon="🛒" label="Refurb Bought"
          value={stats.refurb_bought} sub="items"
          color="bg-teal-50 text-teal-800" />
      </div>

      {/* Credit redemption */}
      <div className="border rounded-2xl p-6 bg-white shadow-sm">
        <h2 className="text-lg font-bold mb-4">Redeem Your Green Credits</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            { label: "₹50 Amazon Coupon",   cost: 100, event: "redeem_amazon_coupon_100" },
            { label: "Prime Month Discount", cost: 200, event: "redeem_prime_discount" },
            { label: "Plant a Tree",         cost: 150, event: "redeem_carbon_offset" },
          ].map((opt) => (
            <div key={opt.event}
                 className="border rounded-xl p-4 text-center hover:border-green-500 transition">
              <p className="font-semibold text-sm">{opt.label}</p>
              <p className="text-green-600 font-bold mt-1">{opt.cost} Credits</p>
              <button
                disabled={stats.green_credits < opt.cost}
                className="mt-2 w-full text-xs bg-green-600 text-white py-1.5
                             rounded-lg disabled:opacity-40 hover:bg-green-700 transition"
              >
                Redeem
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## 🔔 Real-Time Notifications (API Gateway WebSocket)

```python
# server/routers/notifications.py
# Uses AWS API Gateway WebSocket (free 1M messages/mo)
# Local dev: plain WebSocket via FastAPI

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from db.mongo import db
from utils.auth import decode_token
import asyncio

router = APIRouter(prefix="/ws", tags=["ws"])
connections: dict[str, WebSocket] = {}

@router.websocket("/notify/{token}")
async def ws_notify(ws: WebSocket, token: str):
    user = decode_token(token)
    if not user:
        await ws.close(code=1008); return
    uid = user["user_id"]
    await ws.accept()
    connections[uid] = ws
    try:
        while True:
            notifs = list(db.notifications.find(
                {"user_id": uid, "read": False}
            ).sort("created_at", -1).limit(5))
            for n in notifs:
                await ws.send_json({
                    "type": n["type"], "title": n["title"],
                    "body": n["body"],
                    "meta": {k: str(v) for k, v in n.items()
                             if k not in ["_id","user_id","read","created_at"]},
                })
            if notifs:
                db.notifications.update_many(
                    {"user_id": uid, "read": False}, {"$set": {"read": True}})
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        connections.pop(uid, None)
```

---

## 🗄️ MongoDB Schema

```js
// users
{ _id, name, email, location, rating, green_credits, return_rate_pct,
  prime_member, account_age_days, sns_endpoint_arn, credit_history: [] }

// orders
{ _id, user_id, product_id, product_name, product_category,
  product_color, product_size, purchase_date, status,
  p2p_listed, price, product_type: "new"|"refurbished" }

// refurbished_products
{ _id, product_id, name, image, category, refurb_price, original_price,
  vision_grade, repair_count, warranty_months_remaining,
  warranty_months_total, battery_health_pct, seller_rating, seller_id }

// lifecycle_events
{ _id, product_id, user_id, input: {}, result: {action, label, confidence},
  created_at }

// p2p_requests
{ _id, buyer_id, product_id, category, max_budget, condition,
  status: "open"|"matched"|"closed", created_at }

// p2p_listings
{ _id, request_id, seller_id, buyer_id, price, condition,
  description, status: "pending_acceptance"|"accepted"|"completed", created_at }

// return_signals  (aggregated ML signals per product)
{ _id: product_id, return_rate_pct, top_reasons: [], high_risk_profiles: [] }

// notifications
{ _id, user_id, type, title, body, read, created_at, ...meta }

// product_ratings  (for collaborative filtering)
{ _id, user_id, product_id, rating, created_at }
```

---

## 🚀 FastAPI Entry — `server/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import lifecycle, vision, recommendations, credits, p2p, cart, dashboard, notifications

app = FastAPI(title="ReLife AI API", version="2.0.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["https://main.yourid.amplifyapp.com", "http://localhost:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for router in [lifecycle.router, vision.router, recommendations.router,
               credits.router, p2p.router, cart.router,
               dashboard.router, notifications.router]:
    app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "ReLife AI", "version": "2.0.0"}
```

### `server/requirements.txt`

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
motor==3.5.0
boto3==1.34.0
xgboost==2.1.0
scikit-learn==1.5.0
scikit-surprise==1.1.4
pandas==2.2.0
numpy==1.26.0
Pillow==10.3.0
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
pydantic==2.8.0
python-dotenv==1.0.0
```

---

## 🐳 Docker Compose — Local Dev

```yaml
version: "3.9"
services:
  client:
    build: ./client
    ports: ["5173:5173"]
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on: [server]

  server:
    build: ./server
    ports: ["8000:8000"]
    environment:
      - MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/relife
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=us-east-1
      - S3_BUCKET=relife-ai-assets
      - JWT_SECRET=${JWT_SECRET}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./server/ml/models:/app/ml/models

  # Local MongoDB for development
  mongo:
    image: mongo:7
    ports: ["27017:27017"]
    volumes: [mongo_data:/data/db]

volumes:
  mongo_data:
```

---

## ☁️ AWS Deployment — Step by Step

### 1. EC2 t2.micro (FastAPI) — Free 750 hrs/mo

```bash
# SSH into EC2 t2.micro (Amazon Linux 2023)
sudo yum update -y
sudo yum install -y python3.11 python3.11-pip git nginx

# Clone and setup
git clone https://github.com/your-org/relife-ai
cd relife-ai/server
pip3.11 install -r requirements.txt

# Copy trained models (pre-train locally, upload via scp)
scp -i key.pem ml/models/*.pkl ec2-user@EC2_IP:/home/ec2-user/relife-ai/server/ml/models/

# Run with Gunicorn (production ASGI)
pip install gunicorn
gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --daemon

# Nginx reverse proxy config
sudo tee /etc/nginx/conf.d/relife.conf << 'EOF'
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
sudo systemctl restart nginx
```

### 2. AWS Amplify (React) — Free Tier

```yaml
# amplify.yml (place in project root)
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd client && npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: client/dist
    files:
      - '**/*'
  cache:
    paths:
      - client/node_modules/**/*
```

```bash
# Deploy via Amplify CLI
npm install -g @aws-amplify/cli
amplify configure        # set IAM user
amplify init
amplify add hosting      # choose Amplify Hosting
amplify publish          # deploys to https://main.yourid.amplifyapp.com
```

### 3. S3 Bucket for Images

```bash
aws s3 mb s3://relife-ai-assets --region us-east-1
# Set CORS for browser uploads
aws s3api put-bucket-cors --bucket relife-ai-assets --cors-configuration '{
  "CORSRules": [{
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET","PUT","POST"],
    "AllowedHeaders": ["*"]
  }]
}'
```

### 4. DynamoDB Table

```bash
aws dynamodb create-table \
  --table-name relife-user-credits \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
# PAY_PER_REQUEST = free for low hackathon traffic
```

### 5. AWS Cognito (Auth) — Free 50K MAU

```bash
aws cognito-idp create-user-pool \
  --pool-name ReLifeUsers \
  --policies '{"PasswordPolicy":{"MinimumLength":8}}' \
  --region us-east-1

aws cognito-idp create-user-pool-client \
  --user-pool-id <pool-id> \
  --client-name relife-client \
  --no-generate-secret \
  --region us-east-1
```

### 6. Environment Variables

```bash
# .env (never commit)
MONGO_URI=mongodb+srv://user:pass@cluster0.mongodb.net/relife
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET=relife-ai-assets
JWT_SECRET=your-secret-256-bit
COGNITO_USER_POOL_ID=us-east-1_XXXXX
ANTHROPIC_API_KEY=sk-ant-...   # for LLM features (optional)
DYNAMO_TABLE=relife-user-credits
```

---

## 📡 Full API Reference

| Method | Endpoint | Feature | Description |
|--------|----------|---------|-------------|
| POST | `/lifecycle/classify` | 1 | Classify product fate (text inputs) |
| POST | `/lifecycle/classify-with-images` | 1+2 | Vision grade + lifecycle decision |
| POST | `/vision/grade` | 2 | Grade product images only |
| GET | `/recommendations/refurbished` | 3 | Personalised refurbished feed |
| GET | `/recommendations/health-score/{id}` | 3 | Health score for a product |
| POST | `/credits/award/{event}` | 4 | Award green credits |
| POST | `/credits/redeem/{event}` | 4 | Redeem credits for coupons |
| GET | `/credits/balance` | 4 | Current credit balance |
| POST | `/p2p/request` | 5 | Buyer requests used product |
| POST | `/p2p/seller/optin` | 5 | Seller opts in to request |
| GET | `/p2p/matches/{request_id}` | 5 | List seller matches |
| POST | `/cart/analyze` | 6 | Return risk for cart items |
| GET | `/dashboard/sustainability` | 7 | Full sustainability stats |
| WS | `/ws/notify/{token}` | All | Real-time push notifications |

---

## 🛠️ Quick Start

```bash
# Clone
git clone https://github.com/your-org/relife-ai && cd relife-ai

# Backend
cd server
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m ml.train_lifecycle          # train XGBoost model
uvicorn main:app --reload --port 8000

# Frontend
cd ../client
npm install
cp .env.example .env.local           # set VITE_API_URL
npm run dev

# Or run everything with Docker
docker-compose up --build
```

**Live URLs after deployment:**
- Frontend: `https://main.yourid.amplifyapp.com`
- API Docs: `http://EC2_PUBLIC_IP/docs`

---

## 🏆 Hackathon Demo Script

| Step | Action | Output |
|------|--------|--------|
| 1 | Add red dress to cart | ⚠️ "73% return risk — you've returned 3 similar items" |
| 2 | Upload photo of returned laptop | Grade A · 97% confidence · Certified Refurbished recommended |
| 3 | Browse refurbished feed | MacBook Air: Health Score 92/100 · 🏆 Highly Trusted |
| 4 | Request used baby stroller | Notifies 8 sellers via SNS within 2 seconds |
| 5 | Seller opts in via notification | Buyer gets real-time WebSocket alert |
| 6 | Transaction completes | Both earn Green Credits · Dashboard updates |
| 7 | View Sustainability Dashboard | 12 products saved · 48 kg CO₂ · 580 credits |

---

## 🌍 Impact at Scale

| Metric | Value |
|--------|-------|
| Amazon return rate | ~24% of all orders |
| Avg cost per return | ₹350–₹1,200 |
| CO₂ per avoided return | ~2.5 kg |
| Items P2P matchable | ~40% of returns |
| Free tier monthly capacity | ~50K users, 5K vision grades |

---

*ReLife AI · Built for the Amazon Sustainable Commerce Hackathon*
*Stack: React + FastAPI + XGBoost + AWS Rekognition + MongoDB Atlas · Hosted 100% on AWS Free Tier*
