from chalice import Chalice

app = Chalice(app_name='aws-iam-user')


@app.lambda_function()
def create_iam_user(event, context):
    return {'hello': 'world'}

