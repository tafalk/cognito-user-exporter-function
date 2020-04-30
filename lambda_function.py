""" Cognito User Exporter """
import logging
import uuid
from datetime import datetime
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Default Handler"""
    logger.info('post confirmation event triggered')
    # sample event input:
    # {'version': '1', 'region': 'eu-central-1', 'userPoolId': 'eu-central-1_ZDG4xJH34', 'userName': 'vahdet', 'callerContext': {'awsSdkVersion': 'aws-sdk-unknown-unknown', 'clientId': '6nhtgf9qpvq3p1ve8v3f9armci'}, 'triggerSource': 'PostConfirmation_ConfirmSignUp', 'request': {'userAttributes': {'sub': '06b10df6-39fe-4395-a6ba-0943be727801', 'cognito:user_status': 'CONFIRMED', 'email_verified': 'true', 'birthdate': '1989-02-15', 'cognito:email_alias': 'vahdetkeskin@gmail.com', 'email': 'vahdetkeskin@gmail.com'}}, 'response': {}}
    username = event['userName']
    user_pool_id = event['userPoolId']
    email = event['request']['userAttributes']['email']
    birthdate = event['request']['userAttributes']['birthdate']

    logger.info('confirmed signup of user \'%s\' in user pool \'%s\'',
                username, user_pool_id)

    # add user to the default group
    client = boto3.client('cognito-idp')
    client.admin_add_user_to_group(
        UserPoolId=user_pool_id,
        Username=username,
        GroupName=os.environ['COGNITO_USER_GROUP_NAME']
    )

    # put to DynamoDb Users table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_USER_TABLE_NAME'])
    time_now = str(datetime.now())
    table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'username': username,
            'preferredName': username,
            'email': email,
            'birthDate': birthdate,
            'profilePrivacy': 'Protected',
            'allowDirectMesages': True,
            'createdAt': time_now,
            'lastAccess': time_now,
            'accountStatus': 'active'
        }
    )
    return event
