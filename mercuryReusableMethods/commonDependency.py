import inspect
import xml.dom.minidom
import xml.etree.ElementTree as ET
from functools import wraps

import requests
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()


def dump_args(func):
    """
    Decorator to print function call details.

    This includes parameters names and effective values.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        print(f"{func.__module__}.{func.__qualname__} ( {func_args_str} )")
        return func(*args, **kwargs)

    return wrapper


@dump_args
def create_correlation_id(value):
    logger.info({'correlation_id': value})

@dump_args
def log_request_received(event):
    logger.debug(event)

@dump_args
def log_response_received(event):
    logger.debug('Response received', extra={'response': event})

@dump_args
def log_error(exception):
    logger.error('An error occurred', exc_info=exception)

@dump_args
def handle_success(response_body):
    return {
        'statusCode': 200,
        'body': response_body,
    }

@dump_args
def handle_bad_request(error_message):
    return {
        'statusCode': 400,
        'body': error_message,
    }

@dump_args
def handle_unauthorized(error_message):
    return {
        'statusCode': 401,
        'body': error_message,
    }

@dump_args
def handle_forbidden(error_message):
    return {
        'statusCode': 403,
        'body': error_message,
    }

@dump_args
def handle_not_found(error_message):
    return {
        'statusCode': 404,
        'body': error_message,
    }

@dump_args
def handle_not_acceptable(error_message):
    return {
        'statusCode': 406,
        'body': error_message,
    }

@dump_args
def handle_internal_server_error(error_message):
    log_error(error_message)
    return {
        'statusCode': 500,
        'body': 'Internal Server Error',
    }


@tracer.capture_method
def parse_and_print_json(response):
    try:
        json_response = response.json()
        return json_response
    except ValueError:
        return None

@dump_args
@tracer.capture_method
def parse_and_print_xml(response):
    try:
        xml_response = xml.dom.minidom.parseString(response.text)
        pretty_xml = xml_response.toprettyxml()
        return pretty_xml
    except Exception as xml_error:
        return None
    
@dump_args
@tracer.capture_method
def call_api(url, method, data = None, params=None, username= None, password = None):
    try:
        # Add basic authentication if username and password are provided
        auth = (username, password) if username and password else None

        response = requests.request(method, url,data = data, params=params, auth = auth)
        content_type = response.headers.get('content-type', '')

        # Define a mapping of status codes to handler functions
        status_handlers = {
            200: handle_success,
            400: handle_bad_request,
            401: handle_unauthorized,
            403: handle_forbidden,
            404: handle_not_found,
            406: handle_not_acceptable,
        }

        # Default handler for unknown status codes
        default_handler = handle_internal_server_error

        # Get the appropriate handler based on the status code
        status_code = response.status_code
        handler = status_handlers.get(status_code, default_handler)

        # Call the handler function
        result = handler(response.text)

        # Extract common values
        statusCode, body, headers = status_code, result.get('body'), {'Content-Type': 'application/json'}
        messages = response.json().get('messages', [])
        if not any(message.get('messageCode') in ['0', '2000'] for message in messages):
            statusCode = 500

        return statusCode, body, headers

    except requests.exceptions.RequestException as e:
        print(f"Error calling the API: {e}")
        # Handle other errors as internal server error
        result = handle_internal_server_error(str(e))
        return result.get('body'), {'Content-Type': 'application/json'}


def validateEvent(event, expected_keys=None):
    try:
        # Check if "Details" and "Parameters" are present in the request
        assert "Details" in event
        assert "Parameters" in event["Details"]

        # Check if expected_keys are present in the Parameters
        if expected_keys:
            parameters = event["Details"]["Parameters"]
            missing_keys = [key for key in expected_keys if key not in parameters]
            if missing_keys:
                missing_keys_str = ', '.join(missing_keys)
                raise AssertionError(f"Missing keys: {missing_keys_str}")

        return True

    except AssertionError as e:
        # Handle the assertion errors and return False
        print(f"Validation failed. {e}")
        return False
    except Exception as e:
        # Handle other exceptions and return False
        print(f"Unexpected error: {e}")
        return False