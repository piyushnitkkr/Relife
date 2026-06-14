# HackOn with Amazon — Solution Document

**Team Name:** [Your Team Name]
**Hackathon Theme:** Sustainable Commerce / Second-Life Products
**Date:** June 14, 2026

## Team Members

| Name | College / University | Role | Email |
|------|---------------------|------|-------|
| [Member 1] | [College] | Full-Stack + ML | [Email] |
| [Member 2] | [College] | Frontend Dev | [Email] |
| [Member 3] | [College] | Backend + DevOps | [Email] |
| [Member 4] | [College] | AI/ML Engineer | [Email] |

---

## 1. Problem Statement & Relevance

### The Problem

Every year, over 5 billion pounds of returned products end up in landfills globally. In India alone, e-commerce returns cost the industry ₹50,000+ Crore annually. Customers distrust refurbished products (67% avoid them), returns are expensive for everyone, and perfectly usable products are wasted because there's no intelligent system to route them to their next best owner.

### Why It Matters

- **2.6 billion+ online shoppers globally** affected by return friction, wasted money, and guilt
- **Average return rate: 20-30%** (clothing: 40%+) — each return costs ₹200-500 in logistics alone
- **Environmental cost:** Returns generate 24 million metric tons of CO₂ annually — equivalent to 5.1 million cars
- **Cost of inaction:** ₹3 Lakh Crore wasted globally in returned inventory destruction per year

### Theme Alignment

This directly addresses Amazon's vision of sustainable commerce. Instead of treating returns as a loss, ReLife AI transforms them into an opportunity — creating a circular economy inside the shopping experience where every product gets a meaningful second life. Our unique angle: we don't just handle returns *after* they happen — we prevent them *before* purchase and incentivize sustainable behavior throughout.

### What Makes This Novel

**No existing solution combines all 7 systems into one unified platform.** Current approaches are fragmented:
- Amazon Warehouse Deals only handles reselling — no AI decisions, no prevention, no P2P
- OLX/eBay is separate from the shopping ecosystem — no trust, no integration
- No platform uses AI vision grading + lifecycle classification + predictive prevention together

Our insight: **The entire product lifecycle — from pre-purchase warning to post-return routing — can be managed by interconnected AI agents that learn from each other.** A return risk prediction informs the lifecycle engine, which feeds the recommendation system, which drives green credits, which incentivizes the next sustainable purchase. It's a flywheel, not isolated features.

---

## 2. Customer & Solution

### Target Customer

**Primary:** Online shoppers aged 18-45 who buy frequently, occasionally return products, and have idle/unused items at home. They want convenience, trust in what they buy, and feel good about sustainable choices — but won't go out of their way for it.

**Secondary:** Sellers of used/idle products who want a trusted platform to sell without the hassle of OLX/Facebook Marketplace.

### How We Solve It

ReLife AI is an intelligent second-life commerce platform that embeds 7 AI-powered systems directly into the shopping experience:

- **AI Lifecycle Engine (Gemini 3.1):** Instantly decides whether a returned product should be resold, refurbished, donated, exchanged, or recycled — considering repair cost, condition, age, and demand
- **Computer Vision Grading (Gemini 2.5 Flash):** Upload product photos → AI grades condition A/B/C/D with confidence scores, damage detection, and accessory identification
- **Predictive Return Prevention:** Before checkout, AI warns "72% chance you'll return this" based on your history, the product's global return rate, and category patterns
- **P2P Marketplace with Chat:** AI matches buyers with real owners who have idle products in the right lifecycle window — complete with real-time chat and image sharing
- **Green Credits + Sustainability Dashboard:** Every sustainable action earns credits (redeemable for Amazon coupons), tracked in a personal environmental impact dashboard showing CO₂ saved and trees equivalent

### User Workflow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  1. SHOP        │     │  2. DECIDE        │     │  3. IMPACT       │
│                 │     │                   │     │                  │
│ • Browse refurb │────▶│ • Return? AI      │────▶│ • See CO₂ saved  │
│ • See Health    │     │   routes it       │     │ • Earn credits   │
│ • Return risk   │     │ • Sell? P2P match │     │ • Redeem coupons │
│   warning       │     │ • Grade via photo │     │ • Track impact   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Working Prototype

**Live App:** [Your Vercel URL]
**API Docs:** http://[EC2-IP]:8000/docs
**GitHub:** https://github.com/piyushnitkkr/Relife

All 7 features fully functional with real AI (Gemini), real database (MongoDB Atlas), and live deployment on AWS EC2 + Vercel.

---

## 3. Tech Architecture & Scaling

### Architecture

```
┌────────────────────────────────────────────────────┐
│           REACT 18 FRONTEND (Vercel CDN)           │
│   Side Panel Navigation │ All 7 Feature UIs        │
└─────────────────────────┬──────────────────────────┘
                          │ HTTPS (Vercel Proxy)
                ┌─────────▼─────────┐
                │  FastAPI Server    │
                │  (AWS EC2 Docker)  │
                └────┬────┬────┬────┘
                     │    │    │
        ┌────────────┘    │    └────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ MongoDB Atlas│  │ Gemini 2.5   │  │ Gemini 3.1   │
│ (Database)   │  │ Flash (Vision)│  │ Flash Lite   │
│ 200 users    │  │ Image Grade  │  │ (Lifecycle)  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 + Babel (single HTML) | Zero build step, instant deploy, CDN-hosted |
| Backend | FastAPI (Python 3.11) | Async, fast, auto-docs, ML-friendly |
| AI - Vision | Google Gemini 2.5 Flash | Best-in-class image understanding, free tier |
| AI - Reasoning | Groq + Llama 4 Scout 17B | Ultra-fast inference (~200ms), 1000 RPD free, multi-factor reasoning |
| ML Models | Scikit-learn (GradientBoosting + RandomForest) | Lightweight, trains on synthetic data, runs on EC2 |
| Database | MongoDB Atlas (Free M0) | Flexible schema for diverse product/order data |
| Hosting | AWS EC2 (Docker) + Vercel | EC2 for compute, Vercel for CDN + proxy |
| Real-time | HTTP Polling (P2P Chat) | Simple, works over HTTPS, no WebSocket SSL issues |

### Key Algorithms & Complexity

1. **Multi-class Lifecycle Classification:** Groq Llama 4 Scout (17B, 16 experts MoE) with structured decision matrix considering 9 input parameters with explicit weighting (repair cost 25%, product age 25%, return reason 20%, category/seller 15%, accessories/history 15%). Falls back to GradientBoosting ML model with business rule overrides.

2. **Vision-Language Grading:** Gemini 2.5 Flash analyzes raw product images with a structured prompt that enforces A/B/C/D grading scale — detecting damage, accessories, and packaging quality simultaneously.

3. **Return Risk Prediction:** Random Forest trained on 8 features (personal return rate, category patterns, global product signals, account age, price sensitivity). Provides explainable reasons + actionable tips.

4. **Health Score Algorithm:** Weighted composite score (condition 35% + repair history 20% + warranty 20% + seller trust 15% + component health 10%) providing transparent product trustworthiness.

5. **P2P Matching:** Lifecycle-window-aware seller discovery — AI knows baby products are outgrown in 6-36 months, so it targets owners who bought in that window.

### Scaling Strategy

- **Horizontal:** FastAPI + Docker → deploy to ECS/EKS with auto-scaling groups behind ALB
- **Database:** MongoDB Atlas scales to M10/M30 clusters with read replicas; add Redis for credit balance caching
- **AI calls:** Gemini API scales infinitely; add request queuing (SQS) for burst protection
- **CDN:** Frontend already on Vercel's global edge network — zero scaling needed
- **At 1000x:** Add DynamoDB for fast credit reads, S3 for image storage, Lambda for async lifecycle processing, API Gateway for rate limiting

---

## 4. Future Vision

### Where This Goes

In 1-3 years, ReLife AI becomes the **sustainability layer for all of Amazon** — not a separate feature, but embedded intelligence that ensures no product ever reaches a landfill. Every return, every idle item, every purchase decision is touched by our AI ecosystem, creating the world's largest circular commerce engine.

### Roadmap

| Horizon | Milestone | Impact |
|---------|-----------|--------|
| 0-3 mo | Launch 7 features on Amazon India, onboard 10 NGO donation partners, integrate with Amazon Warehouse Deals | 50K users, 10K products given second life |
| 3-6 mo | Multi-language support (Hindi, Tamil, Telugu), seller dashboard for refurb tracking, AR-based vision grading via phone camera | 500K users, ₹2Cr GMV in refurbished sales |
| 6-12 mo | Open API for Flipkart/Meesho integration, B2B enterprise returns management, carbon credit marketplace, predictive demand routing | 5M users, 1M products diverted from landfill |

### Multi-Segment Expansion

| Segment | How ReLife Applies | Path |
|---------|-------------------|------|
| **E-commerce (current)** | Returns lifecycle, P2P, vision grading | Live now |
| **Electronics repair chains** | Vision grading API as-a-service for Croma/Reliance | API licensing, Q2 |
| **Fashion/Apparel** | Size-based return prevention, clothing swap P2P | Category expansion, Q3 |
| **Baby/Kids ecosystem** | Lifecycle-aware resale (items outgrown predictably) | Vertical product, Q3 |
| **Enterprise/B2B** | Bulk returns triage for Amazon warehouses | B2B product, Q4 |
| **Automotive aftermarket** | Part condition grading, second-hand auto parts | New vertical, Year 2 |

### Value Impact

- **30% reduction** in return-related logistics costs (₹500Cr annual savings for Amazon India)
- **2M+ products/year** diverted from landfill at scale
- **₹200Cr** in refurbished product GMV generated on the platform
- **4,000 tonnes CO₂** saved annually (equivalent to planting 180K trees)
- **10M+ users** earning Green Credits, driving repeat sustainable behavior
- **Revenue model:** 5% commission on P2P sales + premium placement for certified refurbished sellers

---

**Links:**
- GitHub: https://github.com/piyushnitkkr/Relife
- Demo Video: [URL]
- Live App: [Your Vercel URL]
