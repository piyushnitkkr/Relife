"""Auth utilities — JWT helpers for hackathon demo."""
from fastapi import Header, HTTPException
from typing import Optional

# Demo: any bearer token whose subject is a valid user_id works.
# In production this would verify against AWS Cognito.

_DEMO_USERS = {
    "demo_user":  {"user_id": "demo_user",  "name": "Alex Kumar"},
    "seller_01":  {"user_id": "seller_01",  "name": "Priya Sharma"},
    "seller_02":  {"user_id": "seller_02",  "name": "Rahul Singh"},
}

_TOKEN_MAP = {
    "demo-token":     "demo_user",
    "seller-token-1": "seller_01",
    "seller-token-2": "seller_02",
}


def decode_token(token: str) -> Optional[dict]:
    uid = _TOKEN_MAP.get(token)
    if uid:
        return _DEMO_USERS[uid]
    # Allow bare user_id as token for simplicity
    if token in _DEMO_USERS:
        return _DEMO_USERS[token]
    return None


async def get_current_user(authorization: str = Header(default="Bearer demo-token")) -> dict:
    token = authorization.removeprefix("Bearer ").strip()
    user = decode_token(token)
    if not user:
        # Default to demo user for hackathon
        return _DEMO_USERS["demo_user"]
    return user
