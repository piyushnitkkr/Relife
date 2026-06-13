"""WebSocket notification router."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from db.mongo import db
from utils.auth import decode_token
import asyncio

router = APIRouter(prefix="/ws", tags=["ws"])
connections: dict[str, WebSocket] = {}


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
