"""Mock DynamoDB table for local development."""


class MockDynamoTable:
    """Simulates DynamoDB user-credits table in-memory."""
    _store: dict = {}

    def update_item(self, Key: dict, UpdateExpression: str,
                    ExpressionAttributeValues: dict, **kwargs):
        uid = Key.get("user_id", "")
        if "ADD green_credits :p" in UpdateExpression:
            self._store[uid] = self._store.get(uid, 0) + ExpressionAttributeValues[":p"]

    def get_item(self, Key: dict):
        uid = Key.get("user_id", "")
        balance = self._store.get(uid, 0)
        return {"Item": {"user_id": uid, "green_credits": balance}}
