"""
ReLife AI — Real AWS DynamoDB connection.
Falls back to mock if boto3 isn't configured.
"""
from config import settings

try:
    import boto3
    _boto3_available = True
except ImportError:
    _boto3_available = False


def _get_dynamo_table():
    """Get real DynamoDB table or fallback mock."""
    if not _boto3_available:
        from db.mock_dynamo import MockDynamoTable
        return MockDynamoTable()

    try:
        dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
        table = dynamodb.Table(settings.DYNAMO_TABLE_NAME)
        # Test connection
        table.table_status
        return table
    except Exception:
        from db.mock_dynamo import MockDynamoTable
        return MockDynamoTable()


dynamo_table = _get_dynamo_table()
