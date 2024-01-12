from aws_cdk import Aspects, Stack, Tags
from constructs import Construct
from cdk_nag import AwsSolutionsChecks, NagSuppressions

from cdk.api_construct import ApiConstruct


class AmzConnectLambdasStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.api = ApiConstruct(
            self,
            'BackendIntegrationLambdas'
        )
        # add security check
        self._add_security_tests()

    def _add_security_tests(self) -> None:
        Aspects.of(self).add(AwsSolutionsChecks(verbose=True))
        # Suppress a specific rule for this resource
        NagSuppressions.add_stack_suppressions(
            self,
            [
                {
                    'id': 'AwsSolutions-IAM4',
                    'reason': 'policy for cloudwatch logs.'
                },
                {
                    'id': 'AwsSolutions-IAM5',
                    'reason': 'policy for cloudwatch logs.'
                },
                {
                    'id': 'AwsSolutions-COG4',
                    'reason': 'not using cognito'
                },
            ],
        )