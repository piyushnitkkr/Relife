# ♻️ ReLife AI — Implementation Guide

## Overview

ReLife AI is an intelligent second-life commerce platform that uses AI to give every returned or unused product a meaningful second life. It consists of 7 interconnected features powered by Google Gemini AI, scikit-learn ML models, and MongoDB Atlas.

---

## Project Structure

```
amazon/
├── frontend/
│   ├── index.html          # Single-file React 18 SPA (all 7 features)
│   └── vercel.json         # Vercel proxy: /api/* → EC2 backend
│
├── server/
│   ├── Dockerfile          # Python 3.11 container for EC2
│   ├── config.py           # Environment config (MongoDB, Gemini, App)
│   ├── main.py             # FastAPI app entry point (28 routes)
│   ├── requirements.txt    # Dependencies (no AWS SDK needed)
│   ├── seed.py             # Generates 200 users + 1000 orders in MongoDB
│   │
│   ├── agents/             # AI/ML Decision Engines
│   │   ├── lifecycle_classifier.py   # Groq Llama 4 Scout + GradientBoosting
│   │   ├── vision_grader.py          # Gemini 2.5 Flash (image analysis)
│   │   ├── return_predictor.py       # RandomForest (return risk)
│   │   ├── recommendation_engine.py  # Health Score algorithm
│   │   └── p2p_ranker.py            # Seller matching & scoring
│   │
│   ├── routers/            # API Endpoints (7 features)
│   │   ├── lifecycle.py    # POST /lifecycle/classify
│   │   ├── vision.py       # POST /vision/grade
│   │   ├── recommendations.py  # GET /recommendations/refurbished
│   │   ├── credits.py      # POST /credits/award, /redeem, GET /balance
│   │   ├── p2p.py          # POST /p2p/request, /seller/optin, chat endpoints
│   │   ├── cart.py         # POST /cart/analyze
│   │   ├── dashboard.py    # GET /dashboard/sustainability
│   │   └── notifications.py # GET /ws/notifications
│   │
│   ├── db/                 # Database Layer
│   │   ├── __init__.py     # Auto-selects real MongoDB or mock
│   │   ├── real_mongo.py   # PyMongo connection to Atlas
│   │   └── mock_db.py      # In-memory mock (no MongoDB needed)
│   │
│   └── utils/
│       └── auth.py         # Demo token auth (3 users)
│
├── .github/workflows/
│   └── deploy.yml          # Auto-deploy to EC2 on push
│
├── solution_document.md    # Hackathon submission document
└── relife_ai_platform.md   # Original blueprint/spec
```

---

## How Each Feature Works

### Feature 1: AI Lifecycle Engine

**File:** `server/agents/lifecycle_classifier.py`

**Flow:**
1. User submits product details (name, category, return reason, age, repair cost, frequency, seller reputation, accessories, days since purchase)
2. Groq API (Llama 4 Scout 17B) receives a structured prompt with a decision matrix and explicit weighting
3. Model considers ALL 9 parameters with weighted importance:
   - Repair cost vs product value: 25%
   - Product age and condition: 25%
   - Return reason: 20%
   - Category demand and seller reputation: 15%
   - Accessories and return history: 15%
4. Returns JSON: `{decision, scores for all 5 options (summing to 100), reasoning}`
5. If Groq fails → falls back to GradientBoosting ML model with business rule overrides
6. Green credits are awarded based on the decision

**Decision Matrix (what the AI considers):**
| Scenario | Decision |
|----------|----------|
| New (<30 days), changed mind, no damage | Resell Certified |
| Minor defect, repair <₹2000, good seller | Refurbish |
| Clothing + size issue, any age | Exchange Marketplace |
| Old (>1 year), baby/kids, functional | Donate to NGO |
| Repair >₹3000, old (>2 years), defective | Recycle |
| Very high repair (>₹5000), any category | Recycle |
| Good condition, 1-6 months old, accessories present | Resell Certified |

**API:** `POST /lifecycle/classify`
**AI Engine:** Groq (Llama 4 Scout 17B-16E) — 30 RPM, 1000 RPD free

---

### Feature 2: Computer Vision Quality Grading

**File:** `server/agents/vision_grader.py`

**Flow:**
1. User uploads 1-3 product photos
2. Images are sent as base64 to Google Gemini 2.5 Flash with a structured grading prompt
3. Gemini analyzes visible damage, accessories, and overall condition
4. Returns grade (A/B/C/D), confidence %, damage types, accessories detected, condition notes
5. If Gemini unavailable → falls back to deterministic simulation

**Grading Scale:**
- A (0-10% damage): Like New → Resell as Certified
- B (10-30%): Minor Wear → Light Refurbishment
- C (30-60%): Refurbishable → Send for Repair
- D (60-100%): Recycle → End of Life

**API:** `POST /vision/grade`
**AI Engine:** Google Gemini 2.5 Flash — real image understanding

---

### Feature 3: Personalized Refurbished Recommendations

**File:** `server/agents/recommendation_engine.py`

**Flow:**
1. Fetches refurbished products from MongoDB
2. Calculates Health Score (0-100) for each product using weighted formula
3. Sorts by score, returns top N with trust badges

**Health Score Formula:**
```
Score = Condition(35%) + Repair History(20%) + Warranty(20%) + Seller Trust(15%) + Component Health(10%)
```

**Trust Badges:**
- ≥85: "🏆 Highly Trusted"
- ≥70: "✅ Verified Good"
- <70: "⚠️ Use with Caution"

**API:** `GET /recommendations/refurbished?category=electronics&n=6`

---

### Feature 4: Green Credits System

**File:** `server/routers/credits.py`

**Flow:**
1. Credits are awarded automatically when users perform sustainable actions
2. Balance stored in MongoDB user document
3. Redeemable for Amazon coupons (₹0.50 per credit)

**Earning Rules:**
| Action | Credits |
|--------|---------|
| Buy refurbished | +50 |
| Donate product | +60 |
| Sell via P2P | +40 |
| Choose recycle | +25 |
| Avoid a return | +20 |
| Upload images | +10 |

**Tiers:** 🌱 Getting Started (<200) → 🌿 Green Member (200+) → 🌳 Eco Champion (500+)

**APIs:** `POST /credits/award/{event}`, `POST /credits/redeem/{event}`, `GET /credits/balance`

---

### Feature 5: P2P Marketplace

**File:** `server/routers/p2p.py`

**Flow:**
1. **Buyer** creates a request (category, budget, condition)
2. Backend queries MongoDB for users who bought that category in the lifecycle window
3. AI ranks sellers by rating + location match
4. **Notifications** sent to sellers (stored in MongoDB)
5. **Seller** sees notification → opts in with price + photos
6. **Chat** opens between buyer and seller (HTTP polling, messages in MongoDB)
7. **End Deal** deletes chat + listing + notifications for both

**Lifecycle Windows:** Baby products (6-36 months), Electronics (18-60 months), Books (1-120 months)

**APIs:** `POST /p2p/request`, `POST /p2p/seller/optin`, `POST /p2p/chat/send`, `GET /p2p/chat/{id}`, `DELETE /p2p/chat/{id}`

---

### Feature 6: Predictive Return Prevention

**File:** `server/agents/return_predictor.py`

**Flow:**
1. When user adds items to cart, frontend calls `/cart/analyze`
2. For each item, RandomForest model predicts return probability
3. Uses 8 features: personal return rate, category return rate, global product signal, category type, size dependency, price, account age, Prime status
4. Returns risk score (0-100%), risk level, explanation, and actionable tip

**Example output:** "72% High Risk — Our AI flagged this because you've returned clothing items before. Tip: Check the size guide carefully."

**API:** `POST /cart/analyze`

---

### Feature 7: Sustainability Dashboard

**File:** `server/routers/dashboard.py`

**Flow:**
1. Aggregates user's activity from MongoDB (lifecycle events, orders, cart events, P2P)
2. Calculates CO₂ saved using per-action constants
3. Returns impact metrics + tier level

**CO₂ Constants:**
- Return avoided: 2.5 kg
- Refurbished bought: 4.0 kg
- Item donated: 1.8 kg
- Item recycled: 1.2 kg

**API:** `GET /dashboard/sustainability`

---

## Deployment Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   User Browser  │────────▶│  Vercel (CDN)    │
│                 │  HTTPS  │  frontend/       │
└─────────────────┘         │  index.html      │
                            └────────┬─────────┘
                                     │ /api/* proxy
                            ┌────────▼─────────┐
                            │  AWS EC2         │
                            │  Docker Container│
                            │  FastAPI :8000   │
                            └───┬────┬────┬────┘
                                │    │    │
                    ┌───────────┘    │    └───────────┐
                    ▼                ▼                ▼
            ┌──────────┐    ┌──────────┐    ┌──────────┐
            │ MongoDB  │    │ Gemini   │    │ Gemini   │
            │ Atlas    │    │ 2.5 Flash│    │ 3.1 Lite │
            │ (Data)   │    │ (Vision) │    │(Lifecycle│
            └──────────┘    └──────────┘    └──────────┘
```

## Running Locally

```bash
cd server
pip install -r requirements.txt
python main.py
# Server starts at http://localhost:8000
# Open frontend/index.html in browser
```

## Deploying to Production

```bash
# On EC2:
cd server
docker build -t relife-server .
docker run -d --name relife -p 8000:8000 --env-file .env --restart always relife-server
docker exec relife python seed.py  # Seed database
```

## Environment Variables

```
APP_ENV=production
MONGO_URI=mongodb+srv://...
GEMINI_API_KEY=AIzaSy...
FRONTEND_URL=https://your-app.vercel.app
PORT=8000
```

## Database Schema (MongoDB Collections)

| Collection | Documents | Purpose |
|-----------|-----------|---------|
| users | 200 | User profiles, credits, history |
| orders | 1000 | Purchase history |
| refurbished_products | 50 | Refurbished catalog |
| lifecycle_events | 300+ | Lifecycle decisions |
| p2p_requests | Dynamic | P2P buy requests |
| p2p_listings | Dynamic | Seller opt-ins |
| p2p_chats | Dynamic | Chat messages |
| notifications | Dynamic | In-app notifications |
| return_signals | 100 | Per-product return data |
| cart_events | 200+ | Return avoidance tracking |
| product_ratings | 500 | For recommendation engine |

## API Endpoints (28 total)

| Method | Path | Feature |
|--------|------|---------|
| GET | / | Serve frontend |
| GET | /health | Health check |
| POST | /lifecycle/classify | F1: Lifecycle decision |
| POST | /lifecycle/classify-with-images | F1+F2: Lifecycle + Vision |
| POST | /vision/grade | F2: Image grading |
| GET | /recommendations/refurbished | F3: Product recommendations |
| GET | /recommendations/health-score/{id} | F3: Single product score |
| POST | /credits/award/{event} | F4: Award credits |
| POST | /credits/redeem/{event} | F4: Redeem credits |
| GET | /credits/balance | F4: Get balance |
| POST | /p2p/request | F5: Create buy request |
| POST | /p2p/seller/optin | F5: Seller opts in |
| GET | /p2p/matches/{id} | F5: Get matches |
| GET | /p2p/my-requests | F5: My requests |
| DELETE | /p2p/request/{id} | F5: Delete request |
| POST | /p2p/chat/send | F5: Send chat message |
| GET | /p2p/chat/{id} | F5: Chat history |
| DELETE | /p2p/chat/{id} | F5: End deal |
| POST | /cart/analyze | F6: Return risk |
| GET | /dashboard/sustainability | F7: Impact stats |
| GET | /ws/notifications | Notifications |
| POST | /ws/notifications/read | Mark read |
