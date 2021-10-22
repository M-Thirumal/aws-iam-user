import uuid
from chalice.test import Client
from app import app


def test_index():
    with Client(app) as client:
        uuid_str = str(uuid.uuid4())
        response = client.lambda_.invoke('create_iam_user', {
            'AccountId': '76576587587',
            'UserName': uuid_str,
            'PolicyName': uuid_str,
            'BucketName': 'bucket-name',
            'FolderName': uuid_str,
            'PolicyARN': [
                'arn:aws:iam::76576587587:policy/app1'
            ]
        })
        assert response.payload is not None
