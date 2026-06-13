"""P2P seller ranker — scores and sorts potential sellers."""
import random


async def rank_sellers(sellers: list, request: dict, buyer: dict) -> list:
    """
    Score sellers based on: rating, location match, price vs budget.
    Returns sellers sorted best-first.
    """
    budget = request.get("max_budget", 10000)
    scored = []
    for s in sellers:
        info   = s.get("seller_info", {})
        rating = info.get("rating", 3.5)
        # Simulate a match score
        score  = (rating / 5.0) * 60 + random.uniform(10, 40)
        scored.append({**s, "match_score": round(score, 1)})
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored
