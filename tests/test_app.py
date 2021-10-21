from chalice.test import Client
from app import app


def test_index():
    with Client(app) as client:
        response = client.lambda_.invoke('create_iam_user', {})
        assert response.payload == {'hello': 'world'}
