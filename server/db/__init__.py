"""
Database layer — auto-selects real MongoDB or in-memory mock
based on whether MONGO_URI is configured.
"""
from config import settings

if settings.use_mock_db:
    from db.mock_db import db
else:
    from db.real_mongo import db

from db.real_dynamo import dynamo_table

__all__ = ["db", "dynamo_table"]
