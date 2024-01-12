import os
import sys
import unittest
from unittest.mock import patch
from functions.GetCustomerProfile.lambda_function import lambda_handler

script_directory = os.path.dirname(os.path.abspath(__file__))
#new_path = script_directory.replace("tests/unit", "get_customer_profile")
#new_path = os.path.abspath(new_path)
#sys.path.append(new_path)

class TestLambdaHandler(unittest.TestCase):
    @patch('functions.GetCustomerProfile.lambda_function.call_api')
    def test_lambda_handler_get_customer_profile_success(self, mock_call_api):
        resource_name = '/test'
        mock_call_api.return_value = [200, '{"testEnvValues": {"baseURL":"true", "environment":"test", "logLevel":"INFO"}}', {'Content-Type': 'application/json'}]

        event = {
                "Details": {
                    "ContactData": {
                    "ContactId": "1234567890",
                    "CustomerEndpoint": {
                        "Address": "+1234567890",
                        "Type": "TELEPHONE_NUMBER"
                    },
                    "InitiationMethod": "INBOUND | OUTBOUND | TRANSFER | CALLBACK",
                    "Attributes": {
                        "customAttribute1": "value1",
                        "customAttribute2": "value2"
                    }
                    },
                    "Parameters": {
                        "keyType": "policyNumber",
                        "keyValue": "NYAP0000000158"
                }
                },
                "Name": "ContactFlowEvent",
                "Type": "InvokeLambdaFunction",
                "Version": "1.0"
                }

        # Call the lambda_handler function
        response = lambda_handler(event, None)

        print("the response from real data is")
        print(response)
        # Assertions for the response
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '{"testEnvValues": {"baseURL":"true", "environment":"test", "logLevel":"INFO"}}')
        self.assertEqual(response['headers'], {'Content-Type': 'application/json'})


if __name__ == '__main__':
    unittest.main()
