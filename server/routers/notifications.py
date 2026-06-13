"""WebSocket notification router + HTTP notifications API."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from db import db
from utils.auth import decode_token, get_current_user
import asyncio

router = APIRouter(prefix="/ws", tags=["ws"])
connections: dict[str, WebSocket] = {}


@router.get("/notifications", tags=["notifications"])
async def get_notifications(user=Depends(get_current_user)):
    """Get unread notifications for the current user."""
    notifs = list(db.notifications.find({"user_id": user["user_id"], "read": False}))
    for n in notifs:
        n.pop("_id", None)
        if "created_at" in n:
            n["created_at"] = str(n["created_at"])
    return {"notifications": notifs, "count": len(notifs)}


@router.post("/notifications/read", tags=["notifications"])
async def mark_read(user=Depends(get_current_user)):
    """Mark all notifications as read."""
    db.notifications.update_many(
        {"user_id": user["user_id"], "read": False},
        {"$set": {"read": True}}
    )
    return {"status": "ok"}


@router.websocket("/notify/{token}")
async def ws_notify(ws: WebSocket, token: str):
    user = decode_token(token) or {"user_id": "demo_user"}
    uid  = user["user_id"]
    await ws.accept()
    connections[uid] = ws
    try:
        while True:
            notifs = list(db.notifications.find({"user_id": uid, "read": False}))
            for n in notifs:
                payload = {k: str(v) if hasattr(v, "isoformat") else v
                           for k, v in n.items() if k != "_id"}
                await ws.send_json(payload)
            if notifs:
                db.notifications.update_many(
                    {"user_id": uid, "read": False}, {"$set": {"read": True}}
                )
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        connections.pop(uid, None)
