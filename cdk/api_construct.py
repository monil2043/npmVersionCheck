from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda import LayerVersion
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
from aws_cdk import aws_ssm as ssm
from cdk.monitoring import CrudMonitoring
import cdk.constants as constants
from aws_cdk import aws_ec2 as ec2
import os

class ApiConstruct(Construct):

    def __init__(self, scope: Construct, id_: str) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        existing_vpc = ec2.Vpc.from_lookup(self, 'dev-AmzConnectInfraVpcStack/dev-AmzconnectInfraVpc',vpc_id = 'vpc-0871a5833d4002d02')
        self.lambda_role = self._build_lambda_role()
        self.common_layer = self._build_common_layer()
        self.appconfig_layer = self._build_appconfig_layer()

        # add all the lambda functions here
        self.fetch_customer_profile = self._add_lambda_fetch_customer_profile(self.lambda_role, existing_vpc)
        # self.save_history = self._add_lambda_save_history(self.lambda_role)
        # self.customers = self._add_lambda_customers(self.lambda_role)
        # self.customerLanguagePreferences = self._add_lambda_customer_language_preferences(self.lambda_role)
        # self.customerPolicies = self._add_lambda_customer_policies(self.lambda_role)
        # self.ivrCallHistory_Create = self._add_lambda_IVRCallHistory_Create(self.lambda_role)
        # self.ivrCallHistory_Edit = self._add_lambda_IVRCallHistory_Edit(self.lambda_role)
        # self.ivrCallHistory_GetById = self._add_lambda_IVRCallHistory_GetById(self.lambda_role)
        # self.ivrIdCards = self._add_lambda_IVRIdCards(self.lambda_role)
        # self.ivrScreenPops_Create = self._add_lambda_IVRScreenPops_Create(self.lambda_role)
        # self.transferNumberLookup = self._add_lambda_transferNumberLookup(self.lambda_role)
        # self.perform_action = self._add_lambda_perform_action(self.lambda_role)

        # this section is for monitoring, add all the lambdas here
        # self.monitoring = CrudMonitoring(self, id_, [self.fetch_customer_profile, self.save_history, 
        #                                              self.customerLanguagePreferences, 
        #                                              self.customerPolicies, self.customers,self.ivrCallHistory_Create,
        #                                              self.ivrCallHistory_Edit,self.ivrCallHistory_GetById,self.ivrIdCards,self.ivrScreenPops_Create,
        #                                              self.perform_action, self.transferNumberLookup])

    def _build_lambda_role(self) -> iam.Role:
        return iam.Role(
            self,
            constants.SERVICE_ROLE_ARN,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamic_configuration':
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=['appconfig:GetLatestConfiguration', 'appconfig:StartConfigurationSession'],
                            resources=['*'],
                            effect=iam.Effect.ALLOW,
                        )
                    ]),
                'appconfig_full_access':  # Add the appConfig_fullAccess policy
                    iam.PolicyDocument(statements=[iam.PolicyStatement(
                        actions=['appconfig:*'],
                        resources=['*'],
                        effect=iam.Effect.ALLOW,
                    )]),
                'ssm_parameter_access':  # New policy for SSM Parameter Store access
                    iam.PolicyDocument(statements=[iam.PolicyStatement(
                        actions=['ssm:GetParameter'],
                        resources=['*'],  # Specify the ARN of the SSM parameter
                        effect=iam.Effect.ALLOW,
                )]),
                'dynamodb_read_access':  # Add DynamoDB read access policy
                    iam.PolicyDocument(statements=[iam.PolicyStatement(
                        actions=['dynamodb:GetItem', 'dynamodb:Query', 'dynamodb:Scan'],
                        resources=['*'],
                        effect=iam.Effect.ALLOW,
                    )])
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}')),
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_VPC_ACCESS_ROLE}'))
            ],
        )

    def _build_common_layer(self) -> PythonLayerVersion:
        return PythonLayerVersion(
            self,
            f'{self.id_}{constants.LAMBDA_LAYER_NAME}',
            entry=constants.COMMON_LAYER_BUILD_FOLDER,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            removal_policy=RemovalPolicy.DESTROY,
        )
    
        # TODO
        # add ARNs by region
        # 'arn:aws:lambda:us-east-1:027255383542:layer:AWS-AppConfig-Extension:113'
        # 'arn:aws:lambda:us-west-2:359756378197:layer:AWS-AppConfig-Extension:146'
    
    def _build_appconfig_layer(self) -> LayerVersion.from_layer_version_arn:
        return LayerVersion.from_layer_version_arn(
            self,
            f'{self.id_}AppConfigLayer',
            layer_version_arn='arn:aws:lambda:us-west-2:359756378197:layer:AWS-AppConfig-Extension:146'
        )
    
    def _add_lambda_fetch_customer_profile(
        self,
        role: iam.Role,
        existing_vpc
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'GetCustomerProfile',
            function_name='GetCustomerProfile',
            runtime=_lambda.Runtime.PYTHON_3_12,
            vpc= existing_vpc,
            code=_lambda.Code.from_asset('functions/GetCustomerProfile'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/CustomerExperience/GetCustomerProfile',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    

    def _add_lambda_save_history(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'SaveHistory',
            function_name='SaveHistory',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/SaveHistory'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/CustomerExperience/SaveHistory',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    

    def _add_lambda_customers(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'Customers',
            function_name='Customers',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/Customers'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/AISIVRService/api/customers',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    

    def _add_lambda_customer_language_preferences(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'CustomerLanguagePreferences',
            function_name='CustomerLanguagePreferences',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/CustomerLanguagePreferences'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/AISIVRService/api/CustomerLanguagePreferences',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    
    def _add_lambda_customer_policies(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'customerpolicies',
            function_name='customerpolicies',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/customerpolicies'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/AISIVRService/api/customerpolicies',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    
    def _add_lambda_IVRCallHistory_Create(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'IVRCallHistory-Create',
            function_name='IVRCallHistory-Create',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/IVRCallHistory-Create'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/AISIVRService/api/IVRCallHistory/Create',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    
    def _add_lambda_IVRCallHistory_Edit(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'IVRCallHistory-Edit',
            function_name='IVRCallHistory-Edit',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/IVRCallHistory-Edit'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/AISIVRService/api/IVRCallHistory/Edit',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    
    def _add_lambda_IVRCallHistory_GetById(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'IVRCallHistory-GetById',
            function_name='IVRCallHistory-GetById',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/IVRCallHistory-GetById'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/AISIVRService/api/IVRCallHistory/GetById',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    

    def _add_lambda_IVRIdCards(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'IVRIdCards',
            function_name='IVRIdCards',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/IVRIdCards'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/AISIVRService/api/IVRIdCards',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    
    def _add_lambda_IVRScreenPops_Create(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'IVRScreenPops-Create',
            function_name='IVRScreenPops-Create',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/IVRScreenPops-Create'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/AISIVRService/api/IVRScreenPops/Create',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    
    def _add_lambda_transferNumberLookup(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'transferNumberLookup',
            function_name='transferNumberLookup',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/TransferNumberLookup'),
            handler='lambda_function.lambda_handler',
            environment={
                'TABLE_NAME': 'Transfer_Number_Lookup_table'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function
    
    def _add_lambda_perform_action(
        self,
        role: iam.Role,
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            'PerformAction',
            function_name='PerformAction',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('functions/PerformAction'),
            handler='lambda_function.lambda_handler',
            environment={
                'RESOURCE_PATH': '/CustomerExperience/PerformAction',
                'MY_PARAMETER_ENV_VAR': '/merc-ins/backend-int/config-store'
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, self.appconfig_layer],
            role=role,
        )
        return lambda_function