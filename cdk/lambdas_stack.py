from aws_cdk import Stack, aws_lambda, RemovalPolicy
from aws_cdk.aws_lambda_python_alpha import PythonFunction, PythonLayerVersion
from constructs import Construct

class AmzConnectLambdasStack(Stack):

    def _create_function(self, integration_name: str, integration_lambda_dependencies: list) :
        integration_lambda = PythonFunction(
            scope=self,
            id=f"{integration_name}",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="handler",
            index=f"{integration_name}.py",  # optional, defaults to 'index.py'
            entry=f"functions/{integration_name}",
            layers=integration_lambda_dependencies,
        )

    def __init__(self, scope: Construct, id: str, ctx: object, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.stage = ctx.stage

        powertools_layer = PythonLayerVersion.from_layer_version_arn(
            self,
            id=f"{self.stage}-lambda-powertools",
            layer_version_arn=f"arn:aws:lambda:{self.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:59",
        )

        utility_layer = PythonLayerVersion(
            scope=self,
            id=f"{self.stage}-integ-utils",
            entry="layers", 
            # https://stackoverflow.com/questions/73060461/create-python-lambda-layer-using-cdk
            # putting the lambda layer in a subfolder 'python' 
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
            removal_policy=RemovalPolicy.DESTROY,
            description="Integration Lambdas utilities",
            layer_version_name=f"{id}_utility_layer_deps"
        )

        self._create_function("hello", [utility_layer, powertools_layer])
        self._create_function("snapshot", [utility_layer, powertools_layer])
        
