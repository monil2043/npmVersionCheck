import json
import os
import boto3
from botocore.exceptions import NoCredentialsError
# from mercuryReusableMethods.commonDependency import (
#     call_api,
#     validateEvent
# )
try:
    from mercuryReusableMethods.commonDependency import (
    call_api,
    validateEvent
)
except ImportError:
    # for local test
    from layers.mercuryReusableMethods.commonDependency import (
    call_api,
    validateEvent
)
from aws_lambda_powertools import Logger, Metrics, Tracer
tracer = Tracer()
logger = Logger()
metrics = Metrics()
resourcePath = os.environ.get('RESOURCE_PATH')
parameter_name = os.environ.get('MY_PARAMETER_ENV_VAR')


def getAppConfigUrl():
    try:
        # Create an SSM client
        ssm_client = boto3.client('ssm')

        # Get the parameter value
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True  # Decrypt the parameter value if it's encrypted
        )

        # Extract the parameter value
        parameter_value = response['Parameter']['Value']

        # Return a response
        return parameter_value

    except NoCredentialsError:
        # Handle credential-related errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'AWS credentials not available'})
        }

    except Exception as e:
        # Handle other exceptions
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    

def getBaseURLAndEnv():
    # Call feature flag to get down the values noted
    baseUrlAndEnv = call_api(getAppConfigUrl(), 'GET')[1]
    config_data = json.loads(baseUrlAndEnv)
    base_url = config_data.get('testEnvValues', {}).get('baseURL', '')
    environment = config_data.get('testEnvValues', {}).get('environment', '')
    log_level = config_data.get('testEnvValues', {}).get('logLevel', '')
    return base_url, environment , log_level

def appendQueryParams(base_url, resource_name=None, params={}):
    # Create the base URL
    if resource_name is not None and resource_name != '':
        url = base_url + resource_name
    else:
        url = base_url

    # Check if params is provided and not empty
    if params:
        # Append query parameters
        url += "?" + "&".join([f"{key}={value}" for key, value in params.items()])

    return url


def createGETCall(event):
    base_url, env , log_level= getBaseURLAndEnv()
    logger.setLevel(log_level)
    resource_name = resourcePath
    #Modify the parameters as per your requirements
    params = {
            "keyType": event['Details']['Parameters']["keyType"],
            "keyValue": event['Details']['Parameters']['keyValue']
        }
    url = appendQueryParams(base_url,resource_name, params)

    statusCodeValue, body, headerValue = (
            call_api(url, 'GET'))
    return {'statusCode': statusCodeValue, 'body': body, 'headers': headerValue}
    



@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    
    if validateEvent(event):
        return createGETCall(event)
    else:
        return {'statusCode': 500, 'body': {"message":"Invalid input event passed"}, 'headers': {'Content-Type': 'application/json'}}



if __name__ == '__main__':
    (lambda_handler(event, None))