import logging
import boto3
import json
from botocore.exceptions import ClientError
from chalice import BadRequestError, ConflictError
from chalice import Chalice

app = Chalice(app_name='aws-iam-user')
app.debug = True
logging.getLogger().setLevel(logging.DEBUG)

iam_client = boto3.client('iam')


@app.lambda_function()
def create_iam_user(event, context):
    logging.debug("Event {}".format(event))
    user_name = event['UserName']
    policy_name = event['PolicyName']
    folder_name = event['FolderName']
    account_id = event['AccountId']
    bucket_name = event['BucketName']
    policy_arn = event['PolicyARN'] if event['PolicyARN'] is not None else []
    logging.debug("Account ID: {}".format(account_id))
    # User
    user = create_user(user_name)
    logging.debug("User {}".format(user))
    # Policy
    policy_arn.append(create_policy(policy_name, bucket_name, folder_name, account_id, user_name))
    # Attaching policy to the user
    if policy_arn is not None:
        for policy in policy_arn:
            logging.debug("policy arn {}".format(policy))
            response = attach_policy(user_name, policy)
            logging.debug("Attach policy response".format(response))
    # Create KEY
    return create_key(user_name, policy_arn)


def create_key(user_name, policy_arn):
    try:
        access_secrete_key = iam_client.create_access_key(
            UserName=user_name
        )
        logging.debug("Key {}".format(access_secrete_key))
    except ClientError as error:
        print('Unexpected error occurred while creating access key... hence cleaning up')
        iam_client.detach_user_policy(
            UserName=user_name,
            PolicyArn=policy_arn
        )
        iam_client.delete_user(UserName=user_name)
        return 'User could not be create', error

    print('User with UserName:{0} got created successfully'.format(user_name))
    return {
        'access_key': access_secrete_key['AccessKey']['AccessKeyId'],
        'secret_key': access_secrete_key['AccessKey']['SecretAccessKey']
    }


def attach_policy(user_name, policy_arn):
    try:
        return iam_client.attach_user_policy(
            UserName=user_name,
            PolicyArn=policy_arn
        )
    except ClientError as error:
        logging.debug('Unexpected error occurred while attaching policy... hence cleaning up', error)
        iam_client.delete_user(UserName=user_name)
        return 'User could not be create', error
    except Exception as e:
        iam_client.delete_user(UserName=user_name)
        logging.error("Error {}".format(e))


def create_policy(policy_name, bucket_name, folder_name, account_id, user_name):
    logging.debug("Bucket Name {}".format(bucket_name))
    logging.debug("Folder Name {}".format(folder_name))
    policy_json = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowStatement1",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketLocation"
                ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::*"
                ]
            },
            {
                "Sid": "AllowStatement2B",
                "Action": [
                    "s3:ListBucket"
                ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::" + bucket_name
                ],
                "Condition": {
                    "StringEquals": {
                        "s3:prefix": [
                            "",
                            "sub-1"
                        ],
                        "s3:delimiter": [
                            "/"
                        ]
                    }
                }
            },
            {
                "Sid": "AllowStatement3",
                "Action": [
                    "s3:ListBucket"
                ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::" + bucket_name
                ],
                "Condition": {
                    "StringLike": {
                        "s3:prefix": [
                            "" + folder_name + "/*"
                        ]
                    }
                }
            },
            {
                "Sid": "AllowStatement4B",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": [
                    "arn:aws:s3:::" + bucket_name + "/" + folder_name + "/*"
                ]
            }
        ]
    }
    logging.debug("Type of policy_json {}".format(type(policy_json)))
    try:
        policy = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_json)
        )
        policy_arn = policy['Policy']['Arn']
        logging.debug('Policy Arn in try : {0}'.format(policy_arn))
        return policy_arn
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            print('Policy already exists.... hence using the same')
            return 'arn:aws:iam::' + account_id + ':policy/' + policy_name
        else:
            print('Unexpected error occurred... cleaning up and exiting from here ')
            iam_client.delete_user(UserName=user_name)
            return error


def create_user(user_name):
    try:
        return iam_client.create_user(
            UserName=user_name,
            Tags=[
                {'Key': 'Owner', 'Value': 'Thirumal'},
                {'Key': 'Created_By', 'Value': 'Generated by Program written by Thirumal'}
            ]
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            warning = 'User {0} is already available'.format(user_name)
            logging.debug(warning)
            raise ConflictError(warning)
        else:
            err = 'Unexpected error occurred... User {0} could not be created'.format(user_name)
            logging.debug(err)
            raise BadRequestError(err)
