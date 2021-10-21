import uuid
from chalice.test import Client
from app import app


def test_index():
    with Client(app) as client:
        uuid_str = str(uuid.uuid4())
        response = client.lambda_.invoke('create_iam_user', {
            'AccountId': '65476567567',
            'UserName': uuid_str,
            'PolicyName': uuid_str,
            'BucketName': 'bucket_name',
            'FolderName': uuid_str
        })
        assert response.payload is not None
