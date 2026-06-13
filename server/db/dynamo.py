"""DynamoDB mock — stores green credits for fast read."""
from db.mongo import db


class _DynamoTable:
    """Simulates DynamoDB user-credits table."""
    _store: dict = {}

    def update_item(self, Key: dict, UpdateExpression: str,
                    ExpressionAttributeValues: dict, **kwargs):
        uid = Key.get("user_id", "")
        if "ADD green_credits :p" in UpdateExpression:
            self._store[uid] = self._store.get(uid, 0) + ExpressionAttributeValues[":p"]

    def get_item(self, Key: dict):
        uid = Key.get("user_id", "")
        # Prefer live MongoDB balance
        user = db.users.find_one({"_id": uid}) or {}
        balance = user.get("green_credits", self._store.get(uid, 0))
        return {"Item": {"user_id": uid, "green_credits": balance}}


dynamo_table = _DynamoTable()
