#!/usr/bin/env python3
import os
import re

from aws_cdk import App, Environment
from boto3 import client, session

from cdk.service_stack import AmzConnectLambdasStack

def modify_stack_name(user_input):
    # Define the regex pattern for a valid AWS CloudFormation stack name
    stack_name_pattern = re.compile(r'^[A-Za-z][A-Za-z0-9-]*$')

    # Remove invalid characters (replace underscores with hyphens)
    modified_name = re.sub(r'[^A-Za-z0-9-]', '-', user_input)

    # Ensure the modified name adheres to the stack name pattern
    if stack_name_pattern.match(modified_name):
        return modified_name
    else:
        # If the modified name still doesn't match, use a default value
        return 'DeployLambdaStack'


account = client('sts').get_caller_identity()['Account']
region = 'us-west-2'
#session.Session().region_name
environment = os.getenv('ENVIRONMENT', 'dev')
app = App()
my_stack = AmzConnectLambdasStack(
    scope=app,
    id=('BuildLambdaStack'),
    env=Environment(account=os.environ.get('AWS_DEFAULT_ACCOUNT', account), region=os.environ.get('AWS_DEFAULT_REGION', region))
)

app.synth()