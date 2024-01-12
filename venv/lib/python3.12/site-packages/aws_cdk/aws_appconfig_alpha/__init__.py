'''
# AWS AppConfig Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

Use AWS AppConfig, a capability of AWS Systems Manager, to create, manage, and quickly deploy application configurations. A configuration is a collection of settings that influence the behavior of your application. You can use AWS AppConfig with applications hosted on Amazon Elastic Compute Cloud (Amazon EC2) instances, AWS Lambda, containers, mobile applications, or IoT devices. To view examples of the types of configurations you can manage by using AWS AppConfig, see [Example configurations](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile.html#appconfig-creating-configuration-and-profile-examples).

## Application

In AWS AppConfig, an application is simply an organizational construct like a folder. This organizational construct has a
relationship with some unit of executable code. For example, you could create an application called MyMobileApp to organize and
manage configuration data for a mobile application installed by your users. Configurations and environments are associated with
the application.

The name and description of an application are optional.

Create a simple application:

```python
appconfig.Application(self, "MyApplication")
```

Create an application with a name and description:

```python
appconfig.Application(self, "MyApplication",
    name="App1",
    description="This is my application created through CDK."
)
```

## Deployment Strategy

A deployment strategy defines how a configuration will roll out. The roll out is defined by four parameters: deployment type,
step percentage, deployment time, and bake time.
See: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html

Deployment strategy with predefined values:

```python
appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
    rollout_strategy=appconfig.RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
)
```

Deployment strategy with custom values:

```python
appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
    rollout_strategy=appconfig.RolloutStrategy.linear(
        growth_factor=20,
        deployment_duration=Duration.minutes(30),
        final_bake_time=Duration.minutes(30)
    )
)
```

## Configuration

A configuration is a higher-level construct that can either be a `HostedConfiguration` (stored internally through AWS
AppConfig) or a `SourcedConfiguration` (stored in an Amazon S3 bucket, AWS Secrets Manager secrets, Systems Manager (SSM)
Parameter Store parameters, SSM documents, or AWS CodePipeline). This construct manages deployments on creation.

### HostedConfiguration

A hosted configuration represents configuration stored in the AWS AppConfig hosted configuration store. A hosted configuration
takes in the configuration content and associated AWS AppConfig application. On construction of a hosted configuration, the
configuration is deployed.

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content.")
)
```

You can define hosted configuration content using any of the following ConfigurationContent methods:

* `fromFile` - Defines the hosted configuration content from a file (you can specify a relative path).
* `fromInlineText` - Defines the hosted configuration from inline text.
* `fromInlineJson` - Defines the hosted configuration from inline JSON.
* `fromInlineYaml` - Defines the hosted configuration from inline YAML.
* `fromInline` - Defines the hosted configuration from user-specified content types.

AWS AppConfig supports the following types of configuration profiles.

* **Feature flag**: Use a feature flag configuration to turn on new features that require a timely deployment, such as a product launch or announcement.
* **Freeform**: Use a freeform configuration to carefully introduce changes to your application.

A hosted configuration with type:

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
    type=appconfig.ConfigurationType.FEATURE_FLAGS
)
```

When you create a configuration and configuration profile, you can specify up to two validators. A validator ensures that your
configuration data is syntactically and semantically correct. You can create validators in either JSON Schema or as an AWS
Lambda function.
See [About validators](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile.html#appconfig-creating-configuration-and-profile-validators) for more information.

When you import a JSON Schema validator from a file, you can pass in a relative path.

A hosted configuration with validators:

```python
# application: appconfig.Application
# fn: lambda.Function


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
    validators=[
        appconfig.JsonSchemaValidator.from_file("schema.json"),
        appconfig.LambdaValidator.from_function(fn)
    ]
)
```

You can attach a deployment strategy (as described in the previous section) to your configuration to specify how you want your
configuration to roll out.

A hosted configuration with a deployment strategy:

```python
# application: appconfig.Application


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
    deployment_strategy=appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
        rollout_strategy=appconfig.RolloutStrategy.linear(
            growth_factor=15,
            deployment_duration=Duration.minutes(30),
            final_bake_time=Duration.minutes(15)
        )
    )
)
```

The `deployTo` parameter is used to specify which environments to deploy the configuration to. If this parameter is not
specified, there will not be a deployment.

A hosted configuration with `deployTo`:

```python
# application: appconfig.Application
# env: appconfig.Environment


appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
    deploy_to=[env]
)
```

To deploy a configuration to an environment after initialization use the `deploy` method:

```python
# application: appconfig.Application
# env: appconfig.Environment


config = appconfig.HostedConfiguration(self, "MyHostedConfiguration",
    application=application,
    content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content.")
)

config.deploy(env)
```

### SourcedConfiguration

A sourced configuration represents configuration stored in an Amazon S3 bucket, AWS Secrets Manager secret, Systems Manager
(SSM) Parameter Store parameter, SSM document, or AWS CodePipeline. A sourced configuration takes in the location source
construct and optionally a version number to deploy. On construction of a sourced configuration, the configuration is deployed
only if a version number is specified.

### S3

Use an Amazon S3 bucket to store a configuration.

```python
# application: appconfig.Application


bucket = s3.Bucket(self, "MyBucket",
    versioned=True
)

appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json")
)
```

Use an encrypted bucket:

```python
# application: appconfig.Application


bucket = s3.Bucket(self, "MyBucket",
    versioned=True,
    encryption=s3.BucketEncryption.KMS
)

appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json")
)
```

### AWS Secrets Manager secret

Use a Secrets Manager secret to store a configuration.

```python
# application: appconfig.Application
# secret: secrets.Secret


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_secret(secret)
)
```

### SSM Parameter Store parameter

Use an SSM parameter to store a configuration.

```python
# application: appconfig.Application
# parameter: ssm.StringParameter


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_parameter(parameter),
    version_number="1"
)
```

### SSM document

Use an SSM document to store a configuration.

```python
# application: appconfig.Application
# document: ssm.CfnDocument


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_cfn_document(document)
)
```

### AWS CodePipeline

Use an AWS CodePipeline pipeline to store a configuration.

```python
# application: appconfig.Application
# pipeline: codepipeline.Pipeline


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_pipeline(pipeline)
)
```

Similar to a hosted configuration, a sourced configuration can optionally take in a type, validators, a `deployTo` parameter, and a deployment strategy.

A sourced configuration with type:

```python
# application: appconfig.Application
# bucket: s3.Bucket


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
    type=appconfig.ConfigurationType.FEATURE_FLAGS,
    name="MyConfig",
    description="This is my sourced configuration from CDK."
)
```

A sourced configuration with validators:

```python
# application: appconfig.Application
# bucket: s3.Bucket
# fn: lambda.Function


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
    validators=[
        appconfig.JsonSchemaValidator.from_file("schema.json"),
        appconfig.LambdaValidator.from_function(fn)
    ]
)
```

A sourced configuration with a deployment strategy:

```python
# application: appconfig.Application
# bucket: s3.Bucket


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
    deployment_strategy=appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
        rollout_strategy=appconfig.RolloutStrategy.linear(
            growth_factor=15,
            deployment_duration=Duration.minutes(30),
            final_bake_time=Duration.minutes(15)
        )
    )
)
```

The `deployTo` parameter is used to specify which environments to deploy the configuration to. If this parameter is not
specified, there will not be a deployment.

A sourced configuration with `deployTo`:

```python
# application: appconfig.Application
# bucket: s3.Bucket
# env: appconfig.Environment


appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
    application=application,
    location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
    deploy_to=[env]
)
```

## Environment

For each AWS AppConfig application, you define one or more environments. An environment is a logical deployment group of AWS
AppConfig targets, such as applications in a Beta or Production environment. You can also define environments for application
subcomponents such as the Web, Mobile, and Back-end components for your application. You can configure Amazon CloudWatch alarms
for each environment. The system monitors alarms during a configuration deployment. If an alarm is triggered, the system rolls
back the configuration.

Basic environment with monitors:

```python
# application: appconfig.Application
# alarm: cloudwatch.Alarm
# composite_alarm: cloudwatch.CompositeAlarm


appconfig.Environment(self, "MyEnvironment",
    application=application,
    monitors=[
        appconfig.Monitor.from_cloud_watch_alarm(alarm),
        appconfig.Monitor.from_cloud_watch_alarm(composite_alarm)
    ]
)
```

Environment monitors also support L1 CfnEnvironment.MonitorsProperty constructs. However, this is not the recommended approach
for CloudWatch alarms because a role will not be auto-generated if not provided.

## Extension

An extension augments your ability to inject logic or behavior at different points during the AWS AppConfig workflow of
creating or deploying a configuration.
See: https://docs.aws.amazon.com/appconfig/latest/userguide/working-with-appconfig-extensions.html

### AWS Lambda destination

Use an AWS Lambda as the event destination for an extension.

```python
# fn: lambda.Function


appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.LambdaDestination(fn)
        )
    ]
)
```

Lambda extension with parameters:

```python
# fn: lambda.Function


appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.LambdaDestination(fn)
        )
    ],
    parameters=[
        appconfig.Parameter.required("testParam", "true"),
        appconfig.Parameter.not_required("testNotRequiredParam")
    ]
)
```

### Amazon Simple Queue Service (SQS) destination

Use a queue as the event destination for an extension.

```python
# queue: sqs.Queue


appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.SqsDestination(queue)
        )
    ]
)
```

### Amazon Simple Notification Service (SNS) destination

Use an SNS topic as the event destination for an extension.

```python
# topic: sns.Topic


appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.SnsDestination(topic)
        )
    ]
)
```

### Amazon EventBridge destination

Use the default event bus as the event destination for an extension.

```python
bus = events.EventBus.from_event_bus_name(self, "MyEventBus", "default")

appconfig.Extension(self, "MyExtension",
    actions=[
        appconfig.Action(
            action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
            event_destination=appconfig.EventBridgeDestination(bus)
        )
    ]
)
```

You can also add extensions and their associations directly by calling `onDeploymentComplete()` or any other action point
method on the AWS AppConfig application, configuration, or environment resource. To add an association to an existing
extension, you can call `addExtension()` on the resource.

Adding an association to an AWS AppConfig application:

```python
# application: appconfig.Application
# extension: appconfig.Extension
# lambda_destination: appconfig.LambdaDestination


application.add_extension(extension)
application.on_deployment_complete(lambda_destination)
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_appconfig as _aws_cdk_aws_appconfig_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_codepipeline as _aws_cdk_aws_codepipeline_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_ceddda9d
import aws_cdk.aws_ssm as _aws_cdk_aws_ssm_ceddda9d
import constructs as _constructs_77d1e7e8


class Action(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appconfig-alpha.Action"):
    '''(experimental) Defines an action for an extension.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # fn: lambda.Function
        
        
        appconfig.Extension(self, "MyExtension",
            actions=[
                appconfig.Action(
                    action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                    event_destination=appconfig.LambdaDestination(fn)
                )
            ]
        )
    '''

    def __init__(
        self,
        *,
        action_points: typing.Sequence["ActionPoint"],
        event_destination: "IEventDestination",
        description: typing.Optional[builtins.str] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        invoke_without_execution_role: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_points: (experimental) The action points that will trigger the extension action.
        :param event_destination: (experimental) The event destination for the action.
        :param description: (experimental) The description for the action. Default: - No description.
        :param execution_role: (experimental) The execution role for the action. Default: - A role is generated.
        :param invoke_without_execution_role: (experimental) The flag that specifies whether or not to create the execution role. If set to true, then the role will not be auto-generated under the assumption there is already the corresponding resource-based policy attached to the event destination. If false, the execution role will be generated if not provided. Default: false
        :param name: (experimental) The name for the action. Default: - A name is generated.

        :stability: experimental
        '''
        props = ActionProps(
            action_points=action_points,
            event_destination=event_destination,
            description=description,
            execution_role=execution_role,
            invoke_without_execution_role=invoke_without_execution_role,
            name=name,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property
    @jsii.member(jsii_name="actionPoints")
    def action_points(self) -> typing.List["ActionPoint"]:
        '''(experimental) The action points that will trigger the extension action.

        :stability: experimental
        '''
        return typing.cast(typing.List["ActionPoint"], jsii.get(self, "actionPoints"))

    @builtins.property
    @jsii.member(jsii_name="eventDestination")
    def event_destination(self) -> "IEventDestination":
        '''(experimental) The event destination for the action.

        :stability: experimental
        '''
        return typing.cast("IEventDestination", jsii.get(self, "eventDestination"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description for the action.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The execution role for the action.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="invokeWithoutExecutionRole")
    def invoke_without_execution_role(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The flag that specifies whether to create the execution role.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "invokeWithoutExecutionRole"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name for the action.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.ActionPoint")
class ActionPoint(enum.Enum):
    '''(experimental) Defines Extension action points.

    :see: https://docs.aws.amazon.com/appconfig/latest/userguide/working-with-appconfig-extensions-about.html#working-with-appconfig-extensions-how-it-works-step-2
    :stability: experimental
    :exampleMetadata: infused

    Example::

        # fn: lambda.Function
        
        
        appconfig.Extension(self, "MyExtension",
            actions=[
                appconfig.Action(
                    action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                    event_destination=appconfig.LambdaDestination(fn)
                )
            ]
        )
    '''

    PRE_CREATE_HOSTED_CONFIGURATION_VERSION = "PRE_CREATE_HOSTED_CONFIGURATION_VERSION"
    '''
    :stability: experimental
    '''
    PRE_START_DEPLOYMENT = "PRE_START_DEPLOYMENT"
    '''
    :stability: experimental
    '''
    ON_DEPLOYMENT_START = "ON_DEPLOYMENT_START"
    '''
    :stability: experimental
    '''
    ON_DEPLOYMENT_STEP = "ON_DEPLOYMENT_STEP"
    '''
    :stability: experimental
    '''
    ON_DEPLOYMENT_BAKING = "ON_DEPLOYMENT_BAKING"
    '''
    :stability: experimental
    '''
    ON_DEPLOYMENT_COMPLETE = "ON_DEPLOYMENT_COMPLETE"
    '''
    :stability: experimental
    '''
    ON_DEPLOYMENT_ROLLED_BACK = "ON_DEPLOYMENT_ROLLED_BACK"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.ActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "action_points": "actionPoints",
        "event_destination": "eventDestination",
        "description": "description",
        "execution_role": "executionRole",
        "invoke_without_execution_role": "invokeWithoutExecutionRole",
        "name": "name",
    },
)
class ActionProps:
    def __init__(
        self,
        *,
        action_points: typing.Sequence[ActionPoint],
        event_destination: "IEventDestination",
        description: typing.Optional[builtins.str] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        invoke_without_execution_role: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the Action construct.

        :param action_points: (experimental) The action points that will trigger the extension action.
        :param event_destination: (experimental) The event destination for the action.
        :param description: (experimental) The description for the action. Default: - No description.
        :param execution_role: (experimental) The execution role for the action. Default: - A role is generated.
        :param invoke_without_execution_role: (experimental) The flag that specifies whether or not to create the execution role. If set to true, then the role will not be auto-generated under the assumption there is already the corresponding resource-based policy attached to the event destination. If false, the execution role will be generated if not provided. Default: false
        :param name: (experimental) The name for the action. Default: - A name is generated.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # fn: lambda.Function
            
            
            appconfig.Extension(self, "MyExtension",
                actions=[
                    appconfig.Action(
                        action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                        event_destination=appconfig.LambdaDestination(fn)
                    )
                ]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46288e96f9fe33c9bb47bbba8fb60684cbbdeea795ddf8471997b3f131bf754b)
            check_type(argname="argument action_points", value=action_points, expected_type=type_hints["action_points"])
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument invoke_without_execution_role", value=invoke_without_execution_role, expected_type=type_hints["invoke_without_execution_role"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action_points": action_points,
            "event_destination": event_destination,
        }
        if description is not None:
            self._values["description"] = description
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if invoke_without_execution_role is not None:
            self._values["invoke_without_execution_role"] = invoke_without_execution_role
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def action_points(self) -> typing.List[ActionPoint]:
        '''(experimental) The action points that will trigger the extension action.

        :stability: experimental
        '''
        result = self._values.get("action_points")
        assert result is not None, "Required property 'action_points' is missing"
        return typing.cast(typing.List[ActionPoint], result)

    @builtins.property
    def event_destination(self) -> "IEventDestination":
        '''(experimental) The event destination for the action.

        :stability: experimental
        '''
        result = self._values.get("event_destination")
        assert result is not None, "Required property 'event_destination' is missing"
        return typing.cast("IEventDestination", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description for the action.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The execution role for the action.

        :default: - A role is generated.

        :stability: experimental
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def invoke_without_execution_role(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The flag that specifies whether or not to create the execution role.

        If set to true, then the role will not be auto-generated under the assumption
        there is already the corresponding resource-based policy attached to the event
        destination. If false, the execution role will be generated if not provided.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("invoke_without_execution_role")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name for the action.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.ApplicationProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "name": "name"},
)
class ApplicationProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the Application construct.

        :param description: (experimental) The description for the application. Default: - No description.
        :param name: (experimental) The name of the application. Default: - A name is generated.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            appconfig.Application(self, "MyApplication",
                name="App1",
                description="This is my application created through CDK."
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cbee3fea531afc63e09b795112d3a192860f492e731257cc8c133ed446715d8)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description for the application.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the application.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigurationContent(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appconfig-alpha.ConfigurationContent",
):
    '''(experimental) Defines the hosted configuration content.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        
        
        appconfig.HostedConfiguration(self, "MyHostedConfiguration",
            application=application,
            content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
            type=appconfig.ConfigurationType.FEATURE_FLAGS
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromFile")
    @builtins.classmethod
    def from_file(
        cls,
        input_path: builtins.str,
        content_type: typing.Optional[builtins.str] = None,
    ) -> "ConfigurationContent":
        '''(experimental) Defines the hosted configuration content from a file.

        :param input_path: The path to the file that defines configuration content.
        :param content_type: The content type of the configuration.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7502b5a45ac7c9e44b72fc76ed509700066911cda074e23bea0f68c7751951c)
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
        return typing.cast("ConfigurationContent", jsii.sinvoke(cls, "fromFile", [input_path, content_type]))

    @jsii.member(jsii_name="fromInline")
    @builtins.classmethod
    def from_inline(
        cls,
        content: builtins.str,
        content_type: typing.Optional[builtins.str] = None,
    ) -> "ConfigurationContent":
        '''(experimental) Defines the hosted configuration content from inline code.

        :param content: The inline code that defines the configuration content.
        :param content_type: The content type of the configuration.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__938076945a03dee347486b3ae6d3b29d530743f9051d57f0e116eb55a25f6a52)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
        return typing.cast("ConfigurationContent", jsii.sinvoke(cls, "fromInline", [content, content_type]))

    @jsii.member(jsii_name="fromInlineJson")
    @builtins.classmethod
    def from_inline_json(
        cls,
        content: builtins.str,
        content_type: typing.Optional[builtins.str] = None,
    ) -> "ConfigurationContent":
        '''(experimental) Defines the hosted configuration content as JSON from inline code.

        :param content: The inline code that defines the configuration content.
        :param content_type: The content type of the configuration.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b97cfe32bafabc8c80832ec71fa30bc172535bb1e5be6622f8bac4dcbece5c)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
        return typing.cast("ConfigurationContent", jsii.sinvoke(cls, "fromInlineJson", [content, content_type]))

    @jsii.member(jsii_name="fromInlineText")
    @builtins.classmethod
    def from_inline_text(cls, content: builtins.str) -> "ConfigurationContent":
        '''(experimental) Defines the hosted configuration content as text from inline code.

        :param content: The inline code that defines the configuration content.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb192081821db66aa5a51d3f2ab560eb9f2321b2c5d128cb17fab16be4951e65)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
        return typing.cast("ConfigurationContent", jsii.sinvoke(cls, "fromInlineText", [content]))

    @jsii.member(jsii_name="fromInlineYaml")
    @builtins.classmethod
    def from_inline_yaml(cls, content: builtins.str) -> "ConfigurationContent":
        '''(experimental) Defines the hosted configuration content as YAML from inline code.

        :param content: The inline code that defines the configuration content.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00cade73f94a6099402ecabdf965dc4b537ad4fa7566f40836237a8715351959)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
        return typing.cast("ConfigurationContent", jsii.sinvoke(cls, "fromInlineYaml", [content]))

    @builtins.property
    @jsii.member(jsii_name="content")
    @abc.abstractmethod
    def content(self) -> builtins.str:
        '''(experimental) The configuration content.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="contentType")
    @abc.abstractmethod
    def content_type(self) -> builtins.str:
        '''(experimental) The configuration content type.

        :stability: experimental
        '''
        ...


class _ConfigurationContentProxy(ConfigurationContent):
    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        '''(experimental) The configuration content.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        '''(experimental) The configuration content type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ConfigurationContent).__jsii_proxy_class__ = lambda : _ConfigurationContentProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.ConfigurationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_key": "deploymentKey",
        "deployment_strategy": "deploymentStrategy",
        "deploy_to": "deployTo",
        "description": "description",
        "name": "name",
        "type": "type",
        "validators": "validators",
    },
)
class ConfigurationOptions:
    def __init__(
        self,
        *,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional["IDeploymentStrategy"] = None,
        deploy_to: typing.Optional[typing.Sequence["IEnvironment"]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional["ConfigurationType"] = None,
        validators: typing.Optional[typing.Sequence["IValidator"]] = None,
    ) -> None:
        '''(experimental) Options for the Configuration construct.

        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appconfig_alpha as appconfig_alpha
            from aws_cdk import aws_kms as kms
            
            # deployment_strategy: appconfig_alpha.DeploymentStrategy
            # environment: appconfig_alpha.Environment
            # key: kms.Key
            # validator: appconfig_alpha.IValidator
            
            configuration_options = appconfig_alpha.ConfigurationOptions(
                deployment_key=key,
                deployment_strategy=deployment_strategy,
                deploy_to=[environment],
                description="description",
                name="name",
                type=appconfig_alpha.ConfigurationType.FREEFORM,
                validators=[validator]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a03005065ab127f6697583f7f4ecf38e1605c1bc30404734b258b1ef55e7bef9)
            check_type(argname="argument deployment_key", value=deployment_key, expected_type=type_hints["deployment_key"])
            check_type(argname="argument deployment_strategy", value=deployment_strategy, expected_type=type_hints["deployment_strategy"])
            check_type(argname="argument deploy_to", value=deploy_to, expected_type=type_hints["deploy_to"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument validators", value=validators, expected_type=type_hints["validators"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if deployment_key is not None:
            self._values["deployment_key"] = deployment_key
        if deployment_strategy is not None:
            self._values["deployment_strategy"] = deployment_strategy
        if deploy_to is not None:
            self._values["deploy_to"] = deploy_to
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type
        if validators is not None:
            self._values["validators"] = validators

    @builtins.property
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key of the configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deployment_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def deployment_strategy(self) -> typing.Optional["IDeploymentStrategy"]:
        '''(experimental) The deployment strategy for the configuration.

        :default:

        - A deployment strategy with the rollout strategy set to
        RolloutStrategy.CANARY_10_PERCENT_20_MINUTES

        :stability: experimental
        '''
        result = self._values.get("deployment_strategy")
        return typing.cast(typing.Optional["IDeploymentStrategy"], result)

    @builtins.property
    def deploy_to(self) -> typing.Optional[typing.List["IEnvironment"]]:
        '''(experimental) The list of environments to deploy the configuration to.

        If this parameter is not specified, then there will be no
        deployment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deploy_to")
        return typing.cast(typing.Optional[typing.List["IEnvironment"]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional["ConfigurationType"]:
        '''(experimental) The type of configuration.

        :default: ConfigurationType.FREEFORM

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["ConfigurationType"], result)

    @builtins.property
    def validators(self) -> typing.Optional[typing.List["IValidator"]]:
        '''(experimental) The validators for the configuration.

        :default: - No validators.

        :stability: experimental
        '''
        result = self._values.get("validators")
        return typing.cast(typing.Optional[typing.List["IValidator"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigurationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.ConfigurationProps",
    jsii_struct_bases=[ConfigurationOptions],
    name_mapping={
        "deployment_key": "deploymentKey",
        "deployment_strategy": "deploymentStrategy",
        "deploy_to": "deployTo",
        "description": "description",
        "name": "name",
        "type": "type",
        "validators": "validators",
        "application": "application",
    },
)
class ConfigurationProps(ConfigurationOptions):
    def __init__(
        self,
        *,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional["IDeploymentStrategy"] = None,
        deploy_to: typing.Optional[typing.Sequence["IEnvironment"]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional["ConfigurationType"] = None,
        validators: typing.Optional[typing.Sequence["IValidator"]] = None,
        application: "IApplication",
    ) -> None:
        '''(experimental) Properties for the Configuration construct.

        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.
        :param application: (experimental) The application associated with the configuration.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appconfig_alpha as appconfig_alpha
            from aws_cdk import aws_kms as kms
            
            # application: appconfig_alpha.Application
            # deployment_strategy: appconfig_alpha.DeploymentStrategy
            # environment: appconfig_alpha.Environment
            # key: kms.Key
            # validator: appconfig_alpha.IValidator
            
            configuration_props = appconfig_alpha.ConfigurationProps(
                application=application,
            
                # the properties below are optional
                deployment_key=key,
                deployment_strategy=deployment_strategy,
                deploy_to=[environment],
                description="description",
                name="name",
                type=appconfig_alpha.ConfigurationType.FREEFORM,
                validators=[validator]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27022aed1f7244394903c06489973edf6a1b616fb6a82022b7cc06e89a9d8738)
            check_type(argname="argument deployment_key", value=deployment_key, expected_type=type_hints["deployment_key"])
            check_type(argname="argument deployment_strategy", value=deployment_strategy, expected_type=type_hints["deployment_strategy"])
            check_type(argname="argument deploy_to", value=deploy_to, expected_type=type_hints["deploy_to"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument validators", value=validators, expected_type=type_hints["validators"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application": application,
        }
        if deployment_key is not None:
            self._values["deployment_key"] = deployment_key
        if deployment_strategy is not None:
            self._values["deployment_strategy"] = deployment_strategy
        if deploy_to is not None:
            self._values["deploy_to"] = deploy_to
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type
        if validators is not None:
            self._values["validators"] = validators

    @builtins.property
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key of the configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deployment_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def deployment_strategy(self) -> typing.Optional["IDeploymentStrategy"]:
        '''(experimental) The deployment strategy for the configuration.

        :default:

        - A deployment strategy with the rollout strategy set to
        RolloutStrategy.CANARY_10_PERCENT_20_MINUTES

        :stability: experimental
        '''
        result = self._values.get("deployment_strategy")
        return typing.cast(typing.Optional["IDeploymentStrategy"], result)

    @builtins.property
    def deploy_to(self) -> typing.Optional[typing.List["IEnvironment"]]:
        '''(experimental) The list of environments to deploy the configuration to.

        If this parameter is not specified, then there will be no
        deployment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deploy_to")
        return typing.cast(typing.Optional[typing.List["IEnvironment"]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional["ConfigurationType"]:
        '''(experimental) The type of configuration.

        :default: ConfigurationType.FREEFORM

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["ConfigurationType"], result)

    @builtins.property
    def validators(self) -> typing.Optional[typing.List["IValidator"]]:
        '''(experimental) The validators for the configuration.

        :default: - No validators.

        :stability: experimental
        '''
        result = self._values.get("validators")
        return typing.cast(typing.Optional[typing.List["IValidator"]], result)

    @builtins.property
    def application(self) -> "IApplication":
        '''(experimental) The application associated with the configuration.

        :stability: experimental
        '''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast("IApplication", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigurationSource(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appconfig-alpha.ConfigurationSource",
):
    '''(experimental) Defines the integrated configuration sources.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        # bucket: s3.Bucket
        
        
        appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
            application=application,
            location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
            type=appconfig.ConfigurationType.FEATURE_FLAGS,
            name="MyConfig",
            description="This is my sourced configuration from CDK."
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromBucket")
    @builtins.classmethod
    def from_bucket(
        cls,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        object_key: builtins.str,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> "ConfigurationSource":
        '''(experimental) Defines configuration content from an Amazon S3 bucket.

        :param bucket: The S3 bucket where the configuration is stored.
        :param object_key: The path to the configuration.
        :param key: The KMS Key that the bucket is encrypted with.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c136a5da041fdfb05b2c0a86bc1874615e76943e8953dfa81ca632280aeffa7)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument object_key", value=object_key, expected_type=type_hints["object_key"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("ConfigurationSource", jsii.sinvoke(cls, "fromBucket", [bucket, object_key, key]))

    @jsii.member(jsii_name="fromCfnDocument")
    @builtins.classmethod
    def from_cfn_document(
        cls,
        document: _aws_cdk_aws_ssm_ceddda9d.CfnDocument,
    ) -> "ConfigurationSource":
        '''(experimental) Defines configuration content from a Systems Manager (SSM) document.

        :param document: The SSM document where the configuration is stored.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cb147eceae8d32d886536f36acf297c8fa3b599ea2f747071a2ee76a8015ab8)
            check_type(argname="argument document", value=document, expected_type=type_hints["document"])
        return typing.cast("ConfigurationSource", jsii.sinvoke(cls, "fromCfnDocument", [document]))

    @jsii.member(jsii_name="fromParameter")
    @builtins.classmethod
    def from_parameter(
        cls,
        parameter: _aws_cdk_aws_ssm_ceddda9d.IParameter,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> "ConfigurationSource":
        '''(experimental) Defines configuration content from a Systems Manager (SSM) Parameter Store parameter.

        :param parameter: The parameter where the configuration is stored.
        :param key: The KMS Key that the secure string is encrypted with.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21c0eeb7ac9307451e9412357d4545c22ad3b112dbd04755b6832b860cb95f64)
            check_type(argname="argument parameter", value=parameter, expected_type=type_hints["parameter"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        return typing.cast("ConfigurationSource", jsii.sinvoke(cls, "fromParameter", [parameter, key]))

    @jsii.member(jsii_name="fromPipeline")
    @builtins.classmethod
    def from_pipeline(
        cls,
        pipeline: _aws_cdk_aws_codepipeline_ceddda9d.IPipeline,
    ) -> "ConfigurationSource":
        '''(experimental) Defines configuration content from AWS CodePipeline.

        :param pipeline: The pipeline where the configuration is stored.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a7609fb6ec54ca7e1300524c441a39dc60f9d37d78666d03edd900aae96b826)
            check_type(argname="argument pipeline", value=pipeline, expected_type=type_hints["pipeline"])
        return typing.cast("ConfigurationSource", jsii.sinvoke(cls, "fromPipeline", [pipeline]))

    @jsii.member(jsii_name="fromSecret")
    @builtins.classmethod
    def from_secret(
        cls,
        secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    ) -> "ConfigurationSource":
        '''(experimental) Defines configuration content from an AWS Secrets Manager secret.

        :param secret: The secret where the configuration is stored.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b8f98a48c7b1026c1f2c4baaa23d27cd0483cd526e66058b6bf7efbf771c366)
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
        return typing.cast("ConfigurationSource", jsii.sinvoke(cls, "fromSecret", [secret]))

    @builtins.property
    @jsii.member(jsii_name="locationUri")
    @abc.abstractmethod
    def location_uri(self) -> builtins.str:
        '''(experimental) The URI of the configuration source.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    @abc.abstractmethod
    def type(self) -> "ConfigurationSourceType":
        '''(experimental) The type of the configuration source.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="key")
    @abc.abstractmethod
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The KMS Key that encrypts the configuration.

        :stability: experimental
        '''
        ...


class _ConfigurationSourceProxy(ConfigurationSource):
    @builtins.property
    @jsii.member(jsii_name="locationUri")
    def location_uri(self) -> builtins.str:
        '''(experimental) The URI of the configuration source.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "locationUri"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "ConfigurationSourceType":
        '''(experimental) The type of the configuration source.

        :stability: experimental
        '''
        return typing.cast("ConfigurationSourceType", jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The KMS Key that encrypts the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "key"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ConfigurationSource).__jsii_proxy_class__ = lambda : _ConfigurationSourceProxy


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.ConfigurationSourceType")
class ConfigurationSourceType(enum.Enum):
    '''(experimental) The configuration source type.

    :stability: experimental
    '''

    S3 = "S3"
    '''
    :stability: experimental
    '''
    SECRETS_MANAGER = "SECRETS_MANAGER"
    '''
    :stability: experimental
    '''
    SSM_PARAMETER = "SSM_PARAMETER"
    '''
    :stability: experimental
    '''
    SSM_DOCUMENT = "SSM_DOCUMENT"
    '''
    :stability: experimental
    '''
    CODE_PIPELINE = "CODE_PIPELINE"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.ConfigurationType")
class ConfigurationType(enum.Enum):
    '''(experimental) The configuration type.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        
        
        appconfig.HostedConfiguration(self, "MyHostedConfiguration",
            application=application,
            content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
            type=appconfig.ConfigurationType.FEATURE_FLAGS
        )
    '''

    FREEFORM = "FREEFORM"
    '''(experimental) Freeform configuration profile.

    Allows you to store your data in the AWS AppConfig
    hosted configuration store or another Systems Manager capability or AWS service that integrates
    with AWS AppConfig.

    :see: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-free-form-configurations-creating.html
    :stability: experimental
    '''
    FEATURE_FLAGS = "FEATURE_FLAGS"
    '''(experimental) Feature flag configuration profile.

    This configuration stores its data
    in the AWS AppConfig hosted configuration store and the URI is simply hosted.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.DeploymentStrategyProps",
    jsii_struct_bases=[],
    name_mapping={
        "rollout_strategy": "rolloutStrategy",
        "description": "description",
        "name": "name",
    },
)
class DeploymentStrategyProps:
    def __init__(
        self,
        *,
        rollout_strategy: "RolloutStrategy",
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for DeploymentStrategy.

        :param rollout_strategy: (experimental) The rollout strategy for the deployment strategy. You can use predefined deployment strategies, such as RolloutStrategy.ALL_AT_ONCE, RolloutStrategy.LINEAR_50_PERCENT_EVERY_30_SECONDS, or RolloutStrategy.CANARY_10_PERCENT_20_MINUTES.
        :param description: (experimental) A description of the deployment strategy. Default: - No description.
        :param name: (experimental) A name for the deployment strategy. Default: - A name is generated.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
                rollout_strategy=appconfig.RolloutStrategy.linear(
                    growth_factor=20,
                    deployment_duration=Duration.minutes(30),
                    final_bake_time=Duration.minutes(30)
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51e828875bce522f87198af3ef36441b4565161ebaf2b89c826ba6694eab24cb)
            check_type(argname="argument rollout_strategy", value=rollout_strategy, expected_type=type_hints["rollout_strategy"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rollout_strategy": rollout_strategy,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def rollout_strategy(self) -> "RolloutStrategy":
        '''(experimental) The rollout strategy for the deployment strategy.

        You can use predefined deployment
        strategies, such as RolloutStrategy.ALL_AT_ONCE, RolloutStrategy.LINEAR_50_PERCENT_EVERY_30_SECONDS,
        or RolloutStrategy.CANARY_10_PERCENT_20_MINUTES.

        :stability: experimental
        '''
        result = self._values.get("rollout_strategy")
        assert result is not None, "Required property 'rollout_strategy' is missing"
        return typing.cast("RolloutStrategy", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the deployment strategy.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the deployment strategy.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeploymentStrategyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.EnvironmentAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "application": "application",
        "environment_id": "environmentId",
        "description": "description",
        "monitors": "monitors",
        "name": "name",
    },
)
class EnvironmentAttributes:
    def __init__(
        self,
        *,
        application: "IApplication",
        environment_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        monitors: typing.Optional[typing.Sequence["Monitor"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes of an existing AWS AppConfig environment to import it.

        :param application: (experimental) The application associated with the environment.
        :param environment_id: (experimental) The ID of the environment.
        :param description: (experimental) The description of the environment. Default: - None.
        :param monitors: (experimental) The monitors for the environment. Default: - None.
        :param name: (experimental) The name of the environment. Default: - None.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appconfig_alpha as appconfig_alpha
            
            # application: appconfig_alpha.Application
            # monitor: appconfig_alpha.Monitor
            
            environment_attributes = appconfig_alpha.EnvironmentAttributes(
                application=application,
                environment_id="environmentId",
            
                # the properties below are optional
                description="description",
                monitors=[monitor],
                name="name"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3723a4291535d1d0cded30ff37bed9ab25f1f441461faf4960998030bb009d4b)
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument environment_id", value=environment_id, expected_type=type_hints["environment_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument monitors", value=monitors, expected_type=type_hints["monitors"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application": application,
            "environment_id": environment_id,
        }
        if description is not None:
            self._values["description"] = description
        if monitors is not None:
            self._values["monitors"] = monitors
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def application(self) -> "IApplication":
        '''(experimental) The application associated with the environment.

        :stability: experimental
        '''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast("IApplication", result)

    @builtins.property
    def environment_id(self) -> builtins.str:
        '''(experimental) The ID of the environment.

        :stability: experimental
        '''
        result = self._values.get("environment_id")
        assert result is not None, "Required property 'environment_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the environment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monitors(self) -> typing.Optional[typing.List["Monitor"]]:
        '''(experimental) The monitors for the environment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("monitors")
        return typing.cast(typing.Optional[typing.List["Monitor"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the environment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvironmentAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.EnvironmentOptions",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "monitors": "monitors",
        "name": "name",
    },
)
class EnvironmentOptions:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        monitors: typing.Optional[typing.Sequence["Monitor"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for the Environment construct.

        :param description: (experimental) The description of the environment. Default: - No description.
        :param monitors: (experimental) The monitors for the environment. Default: - No monitors.
        :param name: (experimental) The name of the environment. Default: - A name is generated.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appconfig_alpha as appconfig_alpha
            
            # monitor: appconfig_alpha.Monitor
            
            environment_options = appconfig_alpha.EnvironmentOptions(
                description="description",
                monitors=[monitor],
                name="name"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5140d041c3695bbfdacfa29a275e5c492198b319932b5b4f7c1355024b07fde)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument monitors", value=monitors, expected_type=type_hints["monitors"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if monitors is not None:
            self._values["monitors"] = monitors
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the environment.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monitors(self) -> typing.Optional[typing.List["Monitor"]]:
        '''(experimental) The monitors for the environment.

        :default: - No monitors.

        :stability: experimental
        '''
        result = self._values.get("monitors")
        return typing.cast(typing.Optional[typing.List["Monitor"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the environment.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvironmentOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.EnvironmentProps",
    jsii_struct_bases=[EnvironmentOptions],
    name_mapping={
        "description": "description",
        "monitors": "monitors",
        "name": "name",
        "application": "application",
    },
)
class EnvironmentProps(EnvironmentOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        monitors: typing.Optional[typing.Sequence["Monitor"]] = None,
        name: typing.Optional[builtins.str] = None,
        application: "IApplication",
    ) -> None:
        '''(experimental) Properties for the Environment construct.

        :param description: (experimental) The description of the environment. Default: - No description.
        :param monitors: (experimental) The monitors for the environment. Default: - No monitors.
        :param name: (experimental) The name of the environment. Default: - A name is generated.
        :param application: (experimental) The application to be associated with the environment.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # application: appconfig.Application
            # alarm: cloudwatch.Alarm
            # composite_alarm: cloudwatch.CompositeAlarm
            
            
            appconfig.Environment(self, "MyEnvironment",
                application=application,
                monitors=[
                    appconfig.Monitor.from_cloud_watch_alarm(alarm),
                    appconfig.Monitor.from_cloud_watch_alarm(composite_alarm)
                ]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0243b92eeec62d4462b9ebe4578a1a5cf6198a8fb56ebd9e2be61d8f4182acf)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument monitors", value=monitors, expected_type=type_hints["monitors"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application": application,
        }
        if description is not None:
            self._values["description"] = description
        if monitors is not None:
            self._values["monitors"] = monitors
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the environment.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monitors(self) -> typing.Optional[typing.List["Monitor"]]:
        '''(experimental) The monitors for the environment.

        :default: - No monitors.

        :stability: experimental
        '''
        result = self._values.get("monitors")
        return typing.cast(typing.Optional[typing.List["Monitor"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the environment.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application(self) -> "IApplication":
        '''(experimental) The application to be associated with the environment.

        :stability: experimental
        '''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast("IApplication", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.ExtensionAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "extension_id": "extensionId",
        "extension_version_number": "extensionVersionNumber",
        "actions": "actions",
        "description": "description",
        "extension_arn": "extensionArn",
        "name": "name",
    },
)
class ExtensionAttributes:
    def __init__(
        self,
        *,
        extension_id: builtins.str,
        extension_version_number: jsii.Number,
        actions: typing.Optional[typing.Sequence[Action]] = None,
        description: typing.Optional[builtins.str] = None,
        extension_arn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes of an existing AWS AppConfig extension to import.

        :param extension_id: (experimental) The ID of the extension.
        :param extension_version_number: (experimental) The version number of the extension.
        :param actions: (experimental) The actions of the extension. Default: - None.
        :param description: (experimental) The description of the extension. Default: - None.
        :param extension_arn: (experimental) The Amazon Resource Name (ARN) of the extension. Default: - The extension ARN is generated.
        :param name: (experimental) The name of the extension. Default: - None.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appconfig_alpha as appconfig_alpha
            
            # action: appconfig_alpha.Action
            
            extension_attributes = appconfig_alpha.ExtensionAttributes(
                extension_id="extensionId",
                extension_version_number=123,
            
                # the properties below are optional
                actions=[action],
                description="description",
                extension_arn="extensionArn",
                name="name"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dca19bc6fb1cff56523990c90cdfc3110a0dc43adc0aa1b408b1aaedeaea231)
            check_type(argname="argument extension_id", value=extension_id, expected_type=type_hints["extension_id"])
            check_type(argname="argument extension_version_number", value=extension_version_number, expected_type=type_hints["extension_version_number"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument extension_arn", value=extension_arn, expected_type=type_hints["extension_arn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "extension_id": extension_id,
            "extension_version_number": extension_version_number,
        }
        if actions is not None:
            self._values["actions"] = actions
        if description is not None:
            self._values["description"] = description
        if extension_arn is not None:
            self._values["extension_arn"] = extension_arn
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def extension_id(self) -> builtins.str:
        '''(experimental) The ID of the extension.

        :stability: experimental
        '''
        result = self._values.get("extension_id")
        assert result is not None, "Required property 'extension_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def extension_version_number(self) -> jsii.Number:
        '''(experimental) The version number of the extension.

        :stability: experimental
        '''
        result = self._values.get("extension_version_number")
        assert result is not None, "Required property 'extension_version_number' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[Action]]:
        '''(experimental) The actions of the extension.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[Action]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the extension.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extension_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Amazon Resource Name (ARN) of the extension.

        :default: - The extension ARN is generated.

        :stability: experimental
        '''
        result = self._values.get("extension_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the extension.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExtensionAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.ExtensionOptions",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "latest_version_number": "latestVersionNumber",
        "name": "name",
        "parameters": "parameters",
    },
)
class ExtensionOptions:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Options for the Extension construct.

        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appconfig_alpha as appconfig_alpha
            
            # parameter: appconfig_alpha.Parameter
            
            extension_options = appconfig_alpha.ExtensionOptions(
                description="description",
                latest_version_number=123,
                name="name",
                parameters=[parameter]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e06ed2a0651b17ebabdc4500ff166928dbaa8501dbbe38ef492b7e71d3664545)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument latest_version_number", value=latest_version_number, expected_type=type_hints["latest_version_number"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if latest_version_number is not None:
            self._values["latest_version_number"] = latest_version_number
        if name is not None:
            self._values["name"] = name
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the extension.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def latest_version_number(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The latest version number of the extension.

        When you create a new version,
        specify the most recent current version number. For example, you create version 3,
        enter 2 for this field.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("latest_version_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the extension.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.List["Parameter"]]:
        '''(experimental) The parameters accepted for the extension.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.List["Parameter"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExtensionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.ExtensionProps",
    jsii_struct_bases=[ExtensionOptions],
    name_mapping={
        "description": "description",
        "latest_version_number": "latestVersionNumber",
        "name": "name",
        "parameters": "parameters",
        "actions": "actions",
    },
)
class ExtensionProps(ExtensionOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
        actions: typing.Sequence[Action],
    ) -> None:
        '''(experimental) Properties for the Extension construct.

        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.
        :param actions: (experimental) The actions for the extension.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # fn: lambda.Function
            
            
            appconfig.Extension(self, "MyExtension",
                actions=[
                    appconfig.Action(
                        action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                        event_destination=appconfig.LambdaDestination(fn)
                    )
                ]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0adb87a6d8e7998dfa19a2f890b7307cc12676acbfb06dcb1c7f3f292b6c99fa)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument latest_version_number", value=latest_version_number, expected_type=type_hints["latest_version_number"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "actions": actions,
        }
        if description is not None:
            self._values["description"] = description
        if latest_version_number is not None:
            self._values["latest_version_number"] = latest_version_number
        if name is not None:
            self._values["name"] = name
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the extension.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def latest_version_number(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The latest version number of the extension.

        When you create a new version,
        specify the most recent current version number. For example, you create version 3,
        enter 2 for this field.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("latest_version_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the extension.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.List["Parameter"]]:
        '''(experimental) The parameters accepted for the extension.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.List["Parameter"]], result)

    @builtins.property
    def actions(self) -> typing.List[Action]:
        '''(experimental) The actions for the extension.

        :stability: experimental
        '''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.List[Action], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExtensionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.GrowthType")
class GrowthType(enum.Enum):
    '''(experimental) Defines the growth type of the deployment strategy.

    :stability: experimental
    '''

    LINEAR = "LINEAR"
    '''(experimental) AWS AppConfig will process the deployment by increments of the growth factor evenly distributed over the deployment.

    :stability: experimental
    '''
    EXPONENTIAL = "EXPONENTIAL"
    '''(experimental) AWS AppConfig will process the deployment exponentially using the following formula: ``G*(2^N)``.

    In this formula, ``G`` is the step percentage specified by the user and ``N``
    is the number of steps until the configuration is deployed to all targets.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.HostedConfigurationOptions",
    jsii_struct_bases=[ConfigurationOptions],
    name_mapping={
        "deployment_key": "deploymentKey",
        "deployment_strategy": "deploymentStrategy",
        "deploy_to": "deployTo",
        "description": "description",
        "name": "name",
        "type": "type",
        "validators": "validators",
        "content": "content",
        "latest_version_number": "latestVersionNumber",
        "version_label": "versionLabel",
    },
)
class HostedConfigurationOptions(ConfigurationOptions):
    def __init__(
        self,
        *,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional["IDeploymentStrategy"] = None,
        deploy_to: typing.Optional[typing.Sequence["IEnvironment"]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence["IValidator"]] = None,
        content: ConfigurationContent,
        latest_version_number: typing.Optional[jsii.Number] = None,
        version_label: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for HostedConfiguration.

        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.
        :param content: (experimental) The content of the hosted configuration.
        :param latest_version_number: (experimental) The latest version number of the hosted configuration. Default: - None.
        :param version_label: (experimental) The version label of the hosted configuration. Default: - None.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appconfig_alpha as appconfig_alpha
            from aws_cdk import aws_kms as kms
            
            # configuration_content: appconfig_alpha.ConfigurationContent
            # deployment_strategy: appconfig_alpha.DeploymentStrategy
            # environment: appconfig_alpha.Environment
            # key: kms.Key
            # validator: appconfig_alpha.IValidator
            
            hosted_configuration_options = appconfig_alpha.HostedConfigurationOptions(
                content=configuration_content,
            
                # the properties below are optional
                deployment_key=key,
                deployment_strategy=deployment_strategy,
                deploy_to=[environment],
                description="description",
                latest_version_number=123,
                name="name",
                type=appconfig_alpha.ConfigurationType.FREEFORM,
                validators=[validator],
                version_label="versionLabel"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32433b560156b021e78132f9bf031c8652ac89c0ca84958ebbb87deb2a83f99f)
            check_type(argname="argument deployment_key", value=deployment_key, expected_type=type_hints["deployment_key"])
            check_type(argname="argument deployment_strategy", value=deployment_strategy, expected_type=type_hints["deployment_strategy"])
            check_type(argname="argument deploy_to", value=deploy_to, expected_type=type_hints["deploy_to"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument validators", value=validators, expected_type=type_hints["validators"])
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument latest_version_number", value=latest_version_number, expected_type=type_hints["latest_version_number"])
            check_type(argname="argument version_label", value=version_label, expected_type=type_hints["version_label"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
        }
        if deployment_key is not None:
            self._values["deployment_key"] = deployment_key
        if deployment_strategy is not None:
            self._values["deployment_strategy"] = deployment_strategy
        if deploy_to is not None:
            self._values["deploy_to"] = deploy_to
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type
        if validators is not None:
            self._values["validators"] = validators
        if latest_version_number is not None:
            self._values["latest_version_number"] = latest_version_number
        if version_label is not None:
            self._values["version_label"] = version_label

    @builtins.property
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key of the configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deployment_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def deployment_strategy(self) -> typing.Optional["IDeploymentStrategy"]:
        '''(experimental) The deployment strategy for the configuration.

        :default:

        - A deployment strategy with the rollout strategy set to
        RolloutStrategy.CANARY_10_PERCENT_20_MINUTES

        :stability: experimental
        '''
        result = self._values.get("deployment_strategy")
        return typing.cast(typing.Optional["IDeploymentStrategy"], result)

    @builtins.property
    def deploy_to(self) -> typing.Optional[typing.List["IEnvironment"]]:
        '''(experimental) The list of environments to deploy the configuration to.

        If this parameter is not specified, then there will be no
        deployment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deploy_to")
        return typing.cast(typing.Optional[typing.List["IEnvironment"]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[ConfigurationType]:
        '''(experimental) The type of configuration.

        :default: ConfigurationType.FREEFORM

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[ConfigurationType], result)

    @builtins.property
    def validators(self) -> typing.Optional[typing.List["IValidator"]]:
        '''(experimental) The validators for the configuration.

        :default: - No validators.

        :stability: experimental
        '''
        result = self._values.get("validators")
        return typing.cast(typing.Optional[typing.List["IValidator"]], result)

    @builtins.property
    def content(self) -> ConfigurationContent:
        '''(experimental) The content of the hosted configuration.

        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(ConfigurationContent, result)

    @builtins.property
    def latest_version_number(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The latest version number of the hosted configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("latest_version_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def version_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version label of the hosted configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("version_label")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostedConfigurationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.HostedConfigurationProps",
    jsii_struct_bases=[ConfigurationProps],
    name_mapping={
        "deployment_key": "deploymentKey",
        "deployment_strategy": "deploymentStrategy",
        "deploy_to": "deployTo",
        "description": "description",
        "name": "name",
        "type": "type",
        "validators": "validators",
        "application": "application",
        "content": "content",
        "latest_version_number": "latestVersionNumber",
        "version_label": "versionLabel",
    },
)
class HostedConfigurationProps(ConfigurationProps):
    def __init__(
        self,
        *,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional["IDeploymentStrategy"] = None,
        deploy_to: typing.Optional[typing.Sequence["IEnvironment"]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence["IValidator"]] = None,
        application: "IApplication",
        content: ConfigurationContent,
        latest_version_number: typing.Optional[jsii.Number] = None,
        version_label: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for HostedConfiguration.

        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.
        :param application: (experimental) The application associated with the configuration.
        :param content: (experimental) The content of the hosted configuration.
        :param latest_version_number: (experimental) The latest version number of the hosted configuration. Default: - None.
        :param version_label: (experimental) The version label of the hosted configuration. Default: - None.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # application: appconfig.Application
            
            
            appconfig.HostedConfiguration(self, "MyHostedConfiguration",
                application=application,
                content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
                type=appconfig.ConfigurationType.FEATURE_FLAGS
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae20008e7170ddf916277cfb81ca2db430b13750ea69944e998e75f56cd3fd30)
            check_type(argname="argument deployment_key", value=deployment_key, expected_type=type_hints["deployment_key"])
            check_type(argname="argument deployment_strategy", value=deployment_strategy, expected_type=type_hints["deployment_strategy"])
            check_type(argname="argument deploy_to", value=deploy_to, expected_type=type_hints["deploy_to"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument validators", value=validators, expected_type=type_hints["validators"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument latest_version_number", value=latest_version_number, expected_type=type_hints["latest_version_number"])
            check_type(argname="argument version_label", value=version_label, expected_type=type_hints["version_label"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application": application,
            "content": content,
        }
        if deployment_key is not None:
            self._values["deployment_key"] = deployment_key
        if deployment_strategy is not None:
            self._values["deployment_strategy"] = deployment_strategy
        if deploy_to is not None:
            self._values["deploy_to"] = deploy_to
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type
        if validators is not None:
            self._values["validators"] = validators
        if latest_version_number is not None:
            self._values["latest_version_number"] = latest_version_number
        if version_label is not None:
            self._values["version_label"] = version_label

    @builtins.property
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key of the configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deployment_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def deployment_strategy(self) -> typing.Optional["IDeploymentStrategy"]:
        '''(experimental) The deployment strategy for the configuration.

        :default:

        - A deployment strategy with the rollout strategy set to
        RolloutStrategy.CANARY_10_PERCENT_20_MINUTES

        :stability: experimental
        '''
        result = self._values.get("deployment_strategy")
        return typing.cast(typing.Optional["IDeploymentStrategy"], result)

    @builtins.property
    def deploy_to(self) -> typing.Optional[typing.List["IEnvironment"]]:
        '''(experimental) The list of environments to deploy the configuration to.

        If this parameter is not specified, then there will be no
        deployment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deploy_to")
        return typing.cast(typing.Optional[typing.List["IEnvironment"]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[ConfigurationType]:
        '''(experimental) The type of configuration.

        :default: ConfigurationType.FREEFORM

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[ConfigurationType], result)

    @builtins.property
    def validators(self) -> typing.Optional[typing.List["IValidator"]]:
        '''(experimental) The validators for the configuration.

        :default: - No validators.

        :stability: experimental
        '''
        result = self._values.get("validators")
        return typing.cast(typing.Optional[typing.List["IValidator"]], result)

    @builtins.property
    def application(self) -> "IApplication":
        '''(experimental) The application associated with the configuration.

        :stability: experimental
        '''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast("IApplication", result)

    @builtins.property
    def content(self) -> ConfigurationContent:
        '''(experimental) The content of the hosted configuration.

        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(ConfigurationContent, result)

    @builtins.property
    def latest_version_number(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The latest version number of the hosted configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("latest_version_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def version_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version label of the hosted configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("version_label")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostedConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-appconfig-alpha.IApplication")
class IApplication(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the application.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="environments")
    def environments(self) -> typing.List["IEnvironment"]:
        '''(experimental) Returns the list of associated environments.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the application.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the application.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        monitors: typing.Optional[typing.Sequence["Monitor"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "IEnvironment":
        '''(experimental) Adds an environment.

        :param id: The name of the environment construct.
        :param description: (experimental) The description of the environment. Default: - No description.
        :param monitors: (experimental) The monitors for the environment. Default: - No monitors.
        :param name: (experimental) The name of the environment. Default: - A name is generated.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addExistingEnvironment")
    def add_existing_environment(self, environment: "IEnvironment") -> None:
        '''(experimental) Adds an existing environment.

        :param environment: The environment.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addHostedConfiguration")
    def add_hosted_configuration(
        self,
        id: builtins.str,
        *,
        content: ConfigurationContent,
        latest_version_number: typing.Optional[jsii.Number] = None,
        version_label: typing.Optional[builtins.str] = None,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional["IDeploymentStrategy"] = None,
        deploy_to: typing.Optional[typing.Sequence["IEnvironment"]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence["IValidator"]] = None,
    ) -> "HostedConfiguration":
        '''(experimental) Adds a hosted configuration.

        :param id: The name of the hosted configuration construct.
        :param content: (experimental) The content of the hosted configuration.
        :param latest_version_number: (experimental) The latest version number of the hosted configuration. Default: - None.
        :param version_label: (experimental) The version label of the hosted configuration. Default: - None.
        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addSourcedConfiguration")
    def add_sourced_configuration(
        self,
        id: builtins.str,
        *,
        location: ConfigurationSource,
        retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        version_number: typing.Optional[builtins.str] = None,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional["IDeploymentStrategy"] = None,
        deploy_to: typing.Optional[typing.Sequence["IEnvironment"]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence["IValidator"]] = None,
    ) -> "SourcedConfiguration":
        '''(experimental) Adds a sourced configuration.

        :param id: The name of the sourced configuration construct.
        :param location: (experimental) The location where the configuration is stored.
        :param retrieval_role: (experimental) The IAM role to retrieve the configuration. Default: - A role is generated.
        :param version_number: (experimental) The version number of the sourced configuration to deploy. If this is not specified, then there will be no deployment. Default: - None.
        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        '''
        ...


class _IApplicationProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appconfig-alpha.IApplication"

    @builtins.property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property
    @jsii.member(jsii_name="environments")
    def environments(self) -> typing.List["IEnvironment"]:
        '''(experimental) Returns the list of associated environments.

        :stability: experimental
        '''
        return typing.cast(typing.List["IEnvironment"], jsii.get(self, "environments"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the application.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the application.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        monitors: typing.Optional[typing.Sequence["Monitor"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "IEnvironment":
        '''(experimental) Adds an environment.

        :param id: The name of the environment construct.
        :param description: (experimental) The description of the environment. Default: - No description.
        :param monitors: (experimental) The monitors for the environment. Default: - No monitors.
        :param name: (experimental) The name of the environment. Default: - A name is generated.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ded273772482567cca9298d2ace15c1c9dbe3de9936f4295a3ea6ce23344201b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = EnvironmentOptions(
            description=description, monitors=monitors, name=name
        )

        return typing.cast("IEnvironment", jsii.invoke(self, "addEnvironment", [id, options]))

    @jsii.member(jsii_name="addExistingEnvironment")
    def add_existing_environment(self, environment: "IEnvironment") -> None:
        '''(experimental) Adds an existing environment.

        :param environment: The environment.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1201d1bf8ee90112a8829dab2d80572c59e2f3838a2224dc3546272098827667)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
        return typing.cast(None, jsii.invoke(self, "addExistingEnvironment", [environment]))

    @jsii.member(jsii_name="addHostedConfiguration")
    def add_hosted_configuration(
        self,
        id: builtins.str,
        *,
        content: ConfigurationContent,
        latest_version_number: typing.Optional[jsii.Number] = None,
        version_label: typing.Optional[builtins.str] = None,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional["IDeploymentStrategy"] = None,
        deploy_to: typing.Optional[typing.Sequence["IEnvironment"]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence["IValidator"]] = None,
    ) -> "HostedConfiguration":
        '''(experimental) Adds a hosted configuration.

        :param id: The name of the hosted configuration construct.
        :param content: (experimental) The content of the hosted configuration.
        :param latest_version_number: (experimental) The latest version number of the hosted configuration. Default: - None.
        :param version_label: (experimental) The version label of the hosted configuration. Default: - None.
        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__345c530a44d22c405803db3af60a51ed00c2c2ad59a9967dba38bc40a9ce8ff5)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = HostedConfigurationOptions(
            content=content,
            latest_version_number=latest_version_number,
            version_label=version_label,
            deployment_key=deployment_key,
            deployment_strategy=deployment_strategy,
            deploy_to=deploy_to,
            description=description,
            name=name,
            type=type,
            validators=validators,
        )

        return typing.cast("HostedConfiguration", jsii.invoke(self, "addHostedConfiguration", [id, options]))

    @jsii.member(jsii_name="addSourcedConfiguration")
    def add_sourced_configuration(
        self,
        id: builtins.str,
        *,
        location: ConfigurationSource,
        retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        version_number: typing.Optional[builtins.str] = None,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional["IDeploymentStrategy"] = None,
        deploy_to: typing.Optional[typing.Sequence["IEnvironment"]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence["IValidator"]] = None,
    ) -> "SourcedConfiguration":
        '''(experimental) Adds a sourced configuration.

        :param id: The name of the sourced configuration construct.
        :param location: (experimental) The location where the configuration is stored.
        :param retrieval_role: (experimental) The IAM role to retrieve the configuration. Default: - A role is generated.
        :param version_number: (experimental) The version number of the sourced configuration to deploy. If this is not specified, then there will be no deployment. Default: - None.
        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bf4f19ff893a70198aa37f46a3fd9e0b47613dac73fc21bcd3b475b8da4d897)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = SourcedConfigurationOptions(
            location=location,
            retrieval_role=retrieval_role,
            version_number=version_number,
            deployment_key=deployment_key,
            deployment_strategy=deployment_strategy,
            deploy_to=deploy_to,
            description=description,
            name=name,
            type=type,
            validators=validators,
        )

        return typing.cast("SourcedConfiguration", jsii.invoke(self, "addSourcedConfiguration", [id, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApplication).__jsii_proxy_class__ = lambda : _IApplicationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appconfig-alpha.IConfiguration")
class IConfiguration(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> IApplication:
        '''(experimental) The application associated with the configuration.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="configurationProfileId")
    def configuration_profile_id(self) -> builtins.str:
        '''(experimental) The ID of the configuration profile.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="deploymentKey")
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key for the configuration.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategy")
    def deployment_strategy(self) -> typing.Optional["IDeploymentStrategy"]:
        '''(experimental) The deployment strategy for the configuration.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="deployTo")
    def deploy_to(self) -> typing.Optional[typing.List["IEnvironment"]]:
        '''(experimental) The environments to deploy to.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[ConfigurationType]:
        '''(experimental) The configuration type.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="validators")
    def validators(self) -> typing.Optional[typing.List["IValidator"]]:
        '''(experimental) The validators for the configuration.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="versionNumber")
    def version_number(self) -> typing.Optional[builtins.str]:
        '''(experimental) The configuration version number.

        :stability: experimental
        '''
        ...


class _IConfigurationProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appconfig-alpha.IConfiguration"

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> IApplication:
        '''(experimental) The application associated with the configuration.

        :stability: experimental
        '''
        return typing.cast(IApplication, jsii.get(self, "application"))

    @builtins.property
    @jsii.member(jsii_name="configurationProfileId")
    def configuration_profile_id(self) -> builtins.str:
        '''(experimental) The ID of the configuration profile.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "configurationProfileId"))

    @builtins.property
    @jsii.member(jsii_name="deploymentKey")
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "deploymentKey"))

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategy")
    def deployment_strategy(self) -> typing.Optional["IDeploymentStrategy"]:
        '''(experimental) The deployment strategy for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["IDeploymentStrategy"], jsii.get(self, "deploymentStrategy"))

    @builtins.property
    @jsii.member(jsii_name="deployTo")
    def deploy_to(self) -> typing.Optional[typing.List["IEnvironment"]]:
        '''(experimental) The environments to deploy to.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List["IEnvironment"]], jsii.get(self, "deployTo"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[ConfigurationType]:
        '''(experimental) The configuration type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ConfigurationType], jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="validators")
    def validators(self) -> typing.Optional[typing.List["IValidator"]]:
        '''(experimental) The validators for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List["IValidator"]], jsii.get(self, "validators"))

    @builtins.property
    @jsii.member(jsii_name="versionNumber")
    def version_number(self) -> typing.Optional[builtins.str]:
        '''(experimental) The configuration version number.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionNumber"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IConfiguration).__jsii_proxy_class__ = lambda : _IConfigurationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appconfig-alpha.IDeploymentStrategy")
class IDeploymentStrategy(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategyArn")
    def deployment_strategy_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the deployment strategy.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategyId")
    def deployment_strategy_id(self) -> builtins.str:
        '''(experimental) The ID of the deployment strategy.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="deploymentDurationInMinutes")
    def deployment_duration_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The deployment duration in minutes.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the deployment strategy.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="finalBakeTimeInMinutes")
    def final_bake_time_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The final bake time in minutes.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="growthFactor")
    def growth_factor(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The growth factor of the deployment strategy.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="growthType")
    def growth_type(self) -> typing.Optional[GrowthType]:
        '''(experimental) The growth type of the deployment strategy.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the deployment strategy.

        :stability: experimental
        '''
        ...


class _IDeploymentStrategyProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appconfig-alpha.IDeploymentStrategy"

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategyArn")
    def deployment_strategy_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the deployment strategy.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "deploymentStrategyArn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategyId")
    def deployment_strategy_id(self) -> builtins.str:
        '''(experimental) The ID of the deployment strategy.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "deploymentStrategyId"))

    @builtins.property
    @jsii.member(jsii_name="deploymentDurationInMinutes")
    def deployment_duration_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The deployment duration in minutes.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deploymentDurationInMinutes"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="finalBakeTimeInMinutes")
    def final_bake_time_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The final bake time in minutes.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "finalBakeTimeInMinutes"))

    @builtins.property
    @jsii.member(jsii_name="growthFactor")
    def growth_factor(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The growth factor of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "growthFactor"))

    @builtins.property
    @jsii.member(jsii_name="growthType")
    def growth_type(self) -> typing.Optional[GrowthType]:
        '''(experimental) The growth type of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[GrowthType], jsii.get(self, "growthType"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDeploymentStrategy).__jsii_proxy_class__ = lambda : _IDeploymentStrategyProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appconfig-alpha.IEnvironment")
class IEnvironment(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application associated to the environment.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="environmentArn")
    def environment_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the environment.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> builtins.str:
        '''(experimental) The ID of the environment.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> typing.Optional[IApplication]:
        '''(experimental) The application associated with the environment.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the environment.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="monitors")
    def monitors(self) -> typing.Optional[typing.List["Monitor"]]:
        '''(experimental) The monitors for the environment.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the environment.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: "IExtension") -> None:
        '''(experimental) Adds an extension association to the environment.

        :param extension: The extension to create an association for.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to the environment.

        :param action_point: The action point which triggers the event.
        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...


class _IEnvironmentProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appconfig-alpha.IEnvironment"

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application associated to the environment.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property
    @jsii.member(jsii_name="environmentArn")
    def environment_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "environmentArn"))

    @builtins.property
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> builtins.str:
        '''(experimental) The ID of the environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "environmentId"))

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> typing.Optional[IApplication]:
        '''(experimental) The application associated with the environment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IApplication], jsii.get(self, "application"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the environment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="monitors")
    def monitors(self) -> typing.Optional[typing.List["Monitor"]]:
        '''(experimental) The monitors for the environment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List["Monitor"]], jsii.get(self, "monitors"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the environment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: "IExtension") -> None:
        '''(experimental) Adds an extension association to the environment.

        :param extension: The extension to create an association for.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ac46fdb36161e4d5ce7f88ea130c9108bd8ba6ddca74a8bedbdd2db1dcb550e)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
        return typing.cast(None, jsii.invoke(self, "addExtension", [extension]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to the environment.

        :param action_point: The action point which triggers the event.
        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb4ec93706f6de52108e02dd9f178c33d3d065b279fc305d736411bf6484289)
            check_type(argname="argument action_point", value=action_point, expected_type=type_hints["action_point"])
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "on", [action_point, event_destination, options]))

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6869fb506b57d6232d5844d2d3d72dd80566b83f5fc0cf46472c31cdb7f43e93)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentBaking", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56fbc6fb391c8f2dd329df242cb73430a52d751b61bb18c0cfce85c56fce1bac)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentComplete", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e202b65f261af5d994327814052fe3be9263268a64816c79e8b00e015fd6e03)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentRolledBack", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00733fd0e9a87966284af81dc4c3bd11fa25d177801f1fcffa665792d1870beb)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStart", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__134d496601d0dded36fa012b2fdc795be5300a63d3bcf08d16f979b4d2f317e9)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStep", [event_destination, options]))

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebba971ad08bf09b517d3ec3c15d4a49621f4d12a780ae42b89993e02473de7b)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preCreateHostedConfigurationVersion", [event_destination, options]))

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: "IEventDestination",
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46989187ed1bb6e3981e270db40bf7aba6abbb31632468b1793b2896c15df51b)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preStartDeployment", [event_destination, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEnvironment).__jsii_proxy_class__ = lambda : _IEnvironmentProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appconfig-alpha.IEventDestination")
class IEventDestination(typing_extensions.Protocol):
    '''(experimental) Implemented by allowed extension event destinations.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="extensionUri")
    def extension_uri(self) -> builtins.str:
        '''(experimental) The URI of the extension event destination.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        '''(experimental) The type of the extension event destination.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="policyDocument")
    def policy_document(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) The IAM policy document to invoke the event destination.

        :stability: experimental
        '''
        ...


class _IEventDestinationProxy:
    '''(experimental) Implemented by allowed extension event destinations.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appconfig-alpha.IEventDestination"

    @builtins.property
    @jsii.member(jsii_name="extensionUri")
    def extension_uri(self) -> builtins.str:
        '''(experimental) The URI of the extension event destination.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionUri"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        '''(experimental) The type of the extension event destination.

        :stability: experimental
        '''
        return typing.cast("SourceType", jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="policyDocument")
    def policy_document(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) The IAM policy document to invoke the event destination.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], jsii.get(self, "policyDocument"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEventDestination).__jsii_proxy_class__ = lambda : _IEventDestinationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appconfig-alpha.IExtensible")
class IExtensible(typing_extensions.Protocol):
    '''(experimental) Defines the extensible base implementation for extension association resources.

    :stability: experimental
    '''

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: "IExtension") -> None:
        '''(experimental) Adds an extension association to the derived resource.

        :param extension: The extension to create an association for.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to the derived resource.

        :param action_point: The action point which triggers the event.
        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        ...


class _IExtensibleProxy:
    '''(experimental) Defines the extensible base implementation for extension association resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appconfig-alpha.IExtensible"

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: "IExtension") -> None:
        '''(experimental) Adds an extension association to the derived resource.

        :param extension: The extension to create an association for.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b9681819f70431eaa2252ef6558d3786043224b911ed27c0d0f0db3313e95ac)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
        return typing.cast(None, jsii.invoke(self, "addExtension", [extension]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to the derived resource.

        :param action_point: The action point which triggers the event.
        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03324aec7fa0a3e37bb7b316301e47f73c6b1994baded6e2fdc523e922e1a62a)
            check_type(argname="argument action_point", value=action_point, expected_type=type_hints["action_point"])
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "on", [action_point, event_destination, options]))

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a916f2f85ba8df6acf76806060fa9d59557b3d7bb2218dc167b4dddebdcedffe)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentBaking", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3e6645b7154c9953be1accc708c29fd4f4af446d189125762a1cea523c27935)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentComplete", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__901d296df706b6491e9e263bd0e4fa2cf3e147f336de94d840f571d9b2aec04e)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentRolledBack", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__039a5ac717b777ef278f54dbda49c2d07b1d820a53f0ea01e461a00b8a8283da)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStart", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b3421f873ed09b510fff0fe6c5fc4bbb73170ec4d6515e1ca1ac85b7ca76dda)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStep", [event_destination, options]))

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65d5f7d0cb5581e1244e2ddc3fdb99125fb0ee731e72a508e19463a2ddac9dca)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preCreateHostedConfigurationVersion", [event_destination, options]))

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence["Parameter"]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca95332d129113e47d1174a792d2f68a28ed1d85e195a415306a9cfd801792f0)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preStartDeployment", [event_destination, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExtensible).__jsii_proxy_class__ = lambda : _IExtensibleProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appconfig-alpha.IExtension")
class IExtension(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="extensionArn")
    def extension_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the extension.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="extensionId")
    def extension_id(self) -> builtins.str:
        '''(experimental) The ID of the extension.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="extensionVersionNumber")
    def extension_version_number(self) -> jsii.Number:
        '''(experimental) The version number of the extension.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.Optional[typing.List[Action]]:
        '''(experimental) The actions for the extension.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the extension.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="latestVersionNumber")
    def latest_version_number(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The latest version number of the extension.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the extension.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.List["Parameter"]]:
        '''(experimental) The parameters of the extension.

        :stability: experimental
        '''
        ...


class _IExtensionProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appconfig-alpha.IExtension"

    @builtins.property
    @jsii.member(jsii_name="extensionArn")
    def extension_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the extension.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionArn"))

    @builtins.property
    @jsii.member(jsii_name="extensionId")
    def extension_id(self) -> builtins.str:
        '''(experimental) The ID of the extension.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionId"))

    @builtins.property
    @jsii.member(jsii_name="extensionVersionNumber")
    def extension_version_number(self) -> jsii.Number:
        '''(experimental) The version number of the extension.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(jsii.Number, jsii.get(self, "extensionVersionNumber"))

    @builtins.property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.Optional[typing.List[Action]]:
        '''(experimental) The actions for the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[Action]], jsii.get(self, "actions"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionNumber")
    def latest_version_number(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The latest version number of the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "latestVersionNumber"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.List["Parameter"]]:
        '''(experimental) The parameters of the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List["Parameter"]], jsii.get(self, "parameters"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExtension).__jsii_proxy_class__ = lambda : _IExtensionProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appconfig-alpha.IValidator")
class IValidator(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        '''(experimental) The content of the validator.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "ValidatorType":
        '''(experimental) The type of validator.

        :stability: experimental
        '''
        ...


class _IValidatorProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appconfig-alpha.IValidator"

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        '''(experimental) The content of the validator.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "ValidatorType":
        '''(experimental) The type of validator.

        :stability: experimental
        '''
        return typing.cast("ValidatorType", jsii.get(self, "type"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IValidator).__jsii_proxy_class__ = lambda : _IValidatorProxy


@jsii.implements(IValidator)
class JsonSchemaValidator(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appconfig-alpha.JsonSchemaValidator",
):
    '''(experimental) Defines a JSON Schema validator.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        # fn: lambda.Function
        
        
        appconfig.HostedConfiguration(self, "MyHostedConfiguration",
            application=application,
            content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
            validators=[
                appconfig.JsonSchemaValidator.from_file("schema.json"),
                appconfig.LambdaValidator.from_function(fn)
            ]
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromFile")
    @builtins.classmethod
    def from_file(cls, input_path: builtins.str) -> "JsonSchemaValidator":
        '''(experimental) Defines a JSON Schema validator from a file.

        :param input_path: The path to the file that defines the validator.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__136f86b4884d57f26b9d59b6da54ae94fde6312376461c60e8d858140b00d43f)
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
        return typing.cast("JsonSchemaValidator", jsii.sinvoke(cls, "fromFile", [input_path]))

    @jsii.member(jsii_name="fromInline")
    @builtins.classmethod
    def from_inline(cls, code: builtins.str) -> "JsonSchemaValidator":
        '''(experimental) Defines a JSON Schema validator from inline code.

        :param code: The inline code that defines the validator.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7288f476e652f7abcef985793193a15f9e580de57ebf517fd278aaafcf588742)
            check_type(argname="argument code", value=code, expected_type=type_hints["code"])
        return typing.cast("JsonSchemaValidator", jsii.sinvoke(cls, "fromInline", [code]))

    @builtins.property
    @jsii.member(jsii_name="content")
    @abc.abstractmethod
    def content(self) -> builtins.str:
        '''(experimental) The content of the validator.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    @abc.abstractmethod
    def type(self) -> "ValidatorType":
        '''(experimental) The type of validator.

        :stability: experimental
        '''
        ...


class _JsonSchemaValidatorProxy(JsonSchemaValidator):
    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        '''(experimental) The content of the validator.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "ValidatorType":
        '''(experimental) The type of validator.

        :stability: experimental
        '''
        return typing.cast("ValidatorType", jsii.get(self, "type"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, JsonSchemaValidator).__jsii_proxy_class__ = lambda : _JsonSchemaValidatorProxy


@jsii.implements(IEventDestination)
class LambdaDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.LambdaDestination",
):
    '''(experimental) Use an AWS Lambda function as an event destination.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # fn: lambda.Function
        
        
        appconfig.Extension(self, "MyExtension",
            actions=[
                appconfig.Action(
                    action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                    event_destination=appconfig.LambdaDestination(fn)
                )
            ]
        )
    '''

    def __init__(self, func: _aws_cdk_aws_lambda_ceddda9d.IFunction) -> None:
        '''
        :param func: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e734e0c6d6a359a840828087e78c1897352f2dea88a313efefab795fc5ee238)
            check_type(argname="argument func", value=func, expected_type=type_hints["func"])
        jsii.create(self.__class__, self, [func])

    @builtins.property
    @jsii.member(jsii_name="extensionUri")
    def extension_uri(self) -> builtins.str:
        '''(experimental) The URI of the extension event destination.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionUri"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        '''(experimental) The type of the extension event destination.

        :stability: experimental
        '''
        return typing.cast("SourceType", jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="policyDocument")
    def policy_document(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) The IAM policy document to invoke the event destination.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], jsii.get(self, "policyDocument"))


@jsii.implements(IValidator)
class LambdaValidator(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appconfig-alpha.LambdaValidator",
):
    '''(experimental) Defines an AWS Lambda validator.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        # fn: lambda.Function
        
        
        appconfig.HostedConfiguration(self, "MyHostedConfiguration",
            application=application,
            content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
            validators=[
                appconfig.JsonSchemaValidator.from_file("schema.json"),
                appconfig.LambdaValidator.from_function(fn)
            ]
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromFunction")
    @builtins.classmethod
    def from_function(
        cls,
        func: _aws_cdk_aws_lambda_ceddda9d.Function,
    ) -> "LambdaValidator":
        '''(experimental) Defines an AWS Lambda validator from a Lambda function.

        This will call
        ``addPermission`` to your function to grant AWS AppConfig permissions.

        :param func: The function that defines the validator.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26ae835e70fab52490538c8b8391d200a506074ceae4b3066414773817e9cd90)
            check_type(argname="argument func", value=func, expected_type=type_hints["func"])
        return typing.cast("LambdaValidator", jsii.sinvoke(cls, "fromFunction", [func]))

    @builtins.property
    @jsii.member(jsii_name="content")
    @abc.abstractmethod
    def content(self) -> builtins.str:
        '''(experimental) The content of the validator.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    @abc.abstractmethod
    def type(self) -> "ValidatorType":
        '''(experimental) The type of validator.

        :stability: experimental
        '''
        ...


class _LambdaValidatorProxy(LambdaValidator):
    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        '''(experimental) The content of the validator.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "ValidatorType":
        '''(experimental) The type of validator.

        :stability: experimental
        '''
        return typing.cast("ValidatorType", jsii.get(self, "type"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, LambdaValidator).__jsii_proxy_class__ = lambda : _LambdaValidatorProxy


class Monitor(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appconfig-alpha.Monitor",
):
    '''(experimental) Defines monitors that will be associated with an AWS AppConfig environment.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        # alarm: cloudwatch.Alarm
        # composite_alarm: cloudwatch.CompositeAlarm
        
        
        appconfig.Environment(self, "MyEnvironment",
            application=application,
            monitors=[
                appconfig.Monitor.from_cloud_watch_alarm(alarm),
                appconfig.Monitor.from_cloud_watch_alarm(composite_alarm)
            ]
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromCfnMonitorsProperty")
    @builtins.classmethod
    def from_cfn_monitors_property(
        cls,
        *,
        alarm_arn: typing.Optional[builtins.str] = None,
        alarm_role_arn: typing.Optional[builtins.str] = None,
    ) -> "Monitor":
        '''(experimental) Creates a Monitor from a CfnEnvironment.MonitorsProperty construct.

        :param alarm_arn: Amazon Resource Name (ARN) of the Amazon CloudWatch alarm.
        :param alarm_role_arn: ARN of an AWS Identity and Access Management (IAM) role for AWS AppConfig to monitor ``AlarmArn`` .

        :stability: experimental
        '''
        monitors_property = _aws_cdk_aws_appconfig_ceddda9d.CfnEnvironment.MonitorsProperty(
            alarm_arn=alarm_arn, alarm_role_arn=alarm_role_arn
        )

        return typing.cast("Monitor", jsii.sinvoke(cls, "fromCfnMonitorsProperty", [monitors_property]))

    @jsii.member(jsii_name="fromCloudWatchAlarm")
    @builtins.classmethod
    def from_cloud_watch_alarm(
        cls,
        alarm: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
        alarm_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> "Monitor":
        '''(experimental) Creates a Monitor from a CloudWatch alarm.

        If the alarm role is not specified, a role will
        be generated.

        :param alarm: The Amazon CloudWatch alarm.
        :param alarm_role: The IAM role for AWS AppConfig to view the alarm state.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7627ea3cc658a47e724a47696800cfc227a7e24ca8ee6a99f50dab4917d2a38f)
            check_type(argname="argument alarm", value=alarm, expected_type=type_hints["alarm"])
            check_type(argname="argument alarm_role", value=alarm_role, expected_type=type_hints["alarm_role"])
        return typing.cast("Monitor", jsii.sinvoke(cls, "fromCloudWatchAlarm", [alarm, alarm_role]))

    @builtins.property
    @jsii.member(jsii_name="alarmArn")
    @abc.abstractmethod
    def alarm_arn(self) -> builtins.str:
        '''(experimental) The alarm ARN for AWS AppConfig to monitor.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="monitorType")
    @abc.abstractmethod
    def monitor_type(self) -> "MonitorType":
        '''(experimental) The type of monitor.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="alarmRoleArn")
    @abc.abstractmethod
    def alarm_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The IAM role ARN for AWS AppConfig to view the alarm state.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="isCompositeAlarm")
    @abc.abstractmethod
    def is_composite_alarm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether a CloudWatch alarm is a composite alarm.

        :stability: experimental
        '''
        ...


class _MonitorProxy(Monitor):
    @builtins.property
    @jsii.member(jsii_name="alarmArn")
    def alarm_arn(self) -> builtins.str:
        '''(experimental) The alarm ARN for AWS AppConfig to monitor.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "alarmArn"))

    @builtins.property
    @jsii.member(jsii_name="monitorType")
    def monitor_type(self) -> "MonitorType":
        '''(experimental) The type of monitor.

        :stability: experimental
        '''
        return typing.cast("MonitorType", jsii.get(self, "monitorType"))

    @builtins.property
    @jsii.member(jsii_name="alarmRoleArn")
    def alarm_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The IAM role ARN for AWS AppConfig to view the alarm state.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmRoleArn"))

    @builtins.property
    @jsii.member(jsii_name="isCompositeAlarm")
    def is_composite_alarm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether a CloudWatch alarm is a composite alarm.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "isCompositeAlarm"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Monitor).__jsii_proxy_class__ = lambda : _MonitorProxy


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.MonitorType")
class MonitorType(enum.Enum):
    '''(experimental) The type of Monitor.

    :stability: experimental
    '''

    CLOUDWATCH = "CLOUDWATCH"
    '''(experimental) A Monitor from a CloudWatch alarm.

    :stability: experimental
    '''
    CFN_MONITORS_PROPERTY = "CFN_MONITORS_PROPERTY"
    '''(experimental) A Monitor from a CfnEnvironment.MonitorsProperty construct.

    :stability: experimental
    '''


class Parameter(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.Parameter",
):
    '''(experimental) Defines a parameter for an extension.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # fn: lambda.Function
        
        
        appconfig.Extension(self, "MyExtension",
            actions=[
                appconfig.Action(
                    action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                    event_destination=appconfig.LambdaDestination(fn)
                )
            ],
            parameters=[
                appconfig.Parameter.required("testParam", "true"),
                appconfig.Parameter.not_required("testNotRequiredParam")
            ]
        )
    '''

    @jsii.member(jsii_name="notRequired")
    @builtins.classmethod
    def not_required(
        cls,
        name: builtins.str,
        value: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> "Parameter":
        '''(experimental) An optional parameter for an extension.

        :param name: The name of the parameter.
        :param value: The value of the parameter.
        :param description: A description for the parameter.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3ac48011ed8e9e256987452651269a593ca438138513a7f69f52c86a141a74e)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        return typing.cast("Parameter", jsii.sinvoke(cls, "notRequired", [name, value, description]))

    @jsii.member(jsii_name="required")
    @builtins.classmethod
    def required(
        cls,
        name: builtins.str,
        value: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> "Parameter":
        '''(experimental) A required parameter for an extension.

        :param name: The name of the parameter.
        :param value: The value of the parameter.
        :param description: A description for the parameter.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__995e35ae3e6d5944133a7f61cb3e95f1a20ef92b0e5b0a60ce4925f95b7345cf)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        return typing.cast("Parameter", jsii.sinvoke(cls, "required", [name, value, description]))

    @builtins.property
    @jsii.member(jsii_name="isRequired")
    def is_required(self) -> builtins.bool:
        '''(experimental) A boolean that indicates if the parameter is required or optional.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isRequired"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the parameter.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the parameter.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Optional[builtins.str]:
        '''(experimental) The value of the parameter.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "value"))


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.Platform")
class Platform(enum.Enum):
    '''(experimental) Defines the platform for the AWS AppConfig Lambda extension.

    :stability: experimental
    '''

    X86_64 = "X86_64"
    '''
    :stability: experimental
    '''
    ARM_64 = "ARM_64"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.PredefinedDeploymentStrategyId")
class PredefinedDeploymentStrategyId(enum.Enum):
    '''(experimental) Defines the deployment strategy ID's of AWS AppConfig predefined strategies.

    :see: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html
    :stability: experimental
    '''

    CANARY_10_PERCENT_20_MINUTES = "CANARY_10_PERCENT_20_MINUTES"
    '''(experimental) **AWS Recommended**.

    This strategy processes the deployment exponentially using a 10% growth factor over 20 minutes.
    AWS AppConfig recommends using this strategy for production deployments because it aligns with AWS best practices
    for configuration deployments.

    :stability: experimental
    '''
    LINEAR_50_PERCENT_EVERY_30_SECONDS = "LINEAR_50_PERCENT_EVERY_30_SECONDS"
    '''(experimental) **Testing/Demonstration**.

    This strategy deploys the configuration to half of all targets every 30 seconds for a
    one-minute deployment. AWS AppConfig recommends using this strategy only for testing or demonstration purposes because
    it has a short duration and bake time.

    :stability: experimental
    '''
    LINEAR_20_PERCENT_EVERY_6_MINUTES = "LINEAR_20_PERCENT_EVERY_6_MINUTES"
    '''(experimental) **AWS Recommended**.

    This strategy deploys the configuration to 20% of all targets every six minutes for a 30 minute deployment.
    AWS AppConfig recommends using this strategy for production deployments because it aligns with AWS best practices
    for configuration deployments.

    :stability: experimental
    '''
    ALL_AT_ONCE = "ALL_AT_ONCE"
    '''(experimental) **Quick**.

    This strategy deploys the configuration to all targets immediately.

    :stability: experimental
    '''


class RolloutStrategy(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appconfig-alpha.RolloutStrategy",
):
    '''(experimental) Defines the rollout strategy for a deployment strategy and includes the growth factor, deployment duration, growth type, and optionally final bake time.

    :see: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html
    :stability: experimental
    :exampleMetadata: infused

    Example::

        appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
            rollout_strategy=appconfig.RolloutStrategy.linear(
                growth_factor=20,
                deployment_duration=Duration.minutes(30),
                final_bake_time=Duration.minutes(30)
            )
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="exponential")
    @builtins.classmethod
    def exponential(
        cls,
        *,
        deployment_duration: _aws_cdk_ceddda9d.Duration,
        growth_factor: jsii.Number,
        final_bake_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> "RolloutStrategy":
        '''(experimental) Build your own exponential rollout strategy.

        :param deployment_duration: (experimental) The deployment duration of the deployment strategy. This defines the total amount of time for a deployment to last.
        :param growth_factor: (experimental) The growth factor of the deployment strategy. This defines the percentage of targets to receive a deployed configuration during each interval.
        :param final_bake_time: (experimental) The final bake time of the deployment strategy. This setting specifies the amount of time AWS AppConfig monitors for Amazon CloudWatch alarms after the configuration has been deployed to 100% of its targets, before considering the deployment to be complete. If an alarm is triggered during this time, AWS AppConfig rolls back the deployment. Default: Duration.minutes(0)

        :stability: experimental
        '''
        props = RolloutStrategyProps(
            deployment_duration=deployment_duration,
            growth_factor=growth_factor,
            final_bake_time=final_bake_time,
        )

        return typing.cast("RolloutStrategy", jsii.sinvoke(cls, "exponential", [props]))

    @jsii.member(jsii_name="linear")
    @builtins.classmethod
    def linear(
        cls,
        *,
        deployment_duration: _aws_cdk_ceddda9d.Duration,
        growth_factor: jsii.Number,
        final_bake_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> "RolloutStrategy":
        '''(experimental) Build your own linear rollout strategy.

        :param deployment_duration: (experimental) The deployment duration of the deployment strategy. This defines the total amount of time for a deployment to last.
        :param growth_factor: (experimental) The growth factor of the deployment strategy. This defines the percentage of targets to receive a deployed configuration during each interval.
        :param final_bake_time: (experimental) The final bake time of the deployment strategy. This setting specifies the amount of time AWS AppConfig monitors for Amazon CloudWatch alarms after the configuration has been deployed to 100% of its targets, before considering the deployment to be complete. If an alarm is triggered during this time, AWS AppConfig rolls back the deployment. Default: Duration.minutes(0)

        :stability: experimental
        '''
        props = RolloutStrategyProps(
            deployment_duration=deployment_duration,
            growth_factor=growth_factor,
            final_bake_time=final_bake_time,
        )

        return typing.cast("RolloutStrategy", jsii.sinvoke(cls, "linear", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALL_AT_ONCE")
    def ALL_AT_ONCE(cls) -> "RolloutStrategy":
        '''(experimental) **Quick**.

        This strategy deploys the configuration to all targets immediately.

        :stability: experimental
        '''
        return typing.cast("RolloutStrategy", jsii.sget(cls, "ALL_AT_ONCE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CANARY_10_PERCENT_20_MINUTES")
    def CANARY_10_PERCENT_20_MINUTES(cls) -> "RolloutStrategy":
        '''(experimental) **AWS Recommended**.

        This strategy processes the deployment exponentially using a 10% growth factor over 20 minutes.
        AWS AppConfig recommends using this strategy for production deployments because it aligns with AWS best practices
        for configuration deployments.

        :stability: experimental
        '''
        return typing.cast("RolloutStrategy", jsii.sget(cls, "CANARY_10_PERCENT_20_MINUTES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="LINEAR_20_PERCENT_EVERY_6_MINUTES")
    def LINEAR_20_PERCENT_EVERY_6_MINUTES(cls) -> "RolloutStrategy":
        '''(experimental) **AWS Recommended**.

        This strategy deploys the configuration to 20% of all targets every six minutes for a 30 minute deployment.
        AWS AppConfig recommends using this strategy for production deployments because it aligns with AWS best practices
        for configuration deployments.

        :stability: experimental
        '''
        return typing.cast("RolloutStrategy", jsii.sget(cls, "LINEAR_20_PERCENT_EVERY_6_MINUTES"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="LINEAR_50_PERCENT_EVERY_30_SECONDS")
    def LINEAR_50_PERCENT_EVERY_30_SECONDS(cls) -> "RolloutStrategy":
        '''(experimental) **Testing/Demonstration**.

        This strategy deploys the configuration to half of all targets every 30 seconds for a
        one-minute deployment. AWS AppConfig recommends using this strategy only for testing or demonstration purposes because
        it has a short duration and bake time.

        :stability: experimental
        '''
        return typing.cast("RolloutStrategy", jsii.sget(cls, "LINEAR_50_PERCENT_EVERY_30_SECONDS"))

    @builtins.property
    @jsii.member(jsii_name="deploymentDuration")
    @abc.abstractmethod
    def deployment_duration(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The deployment duration of the rollout strategy.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="growthFactor")
    @abc.abstractmethod
    def growth_factor(self) -> jsii.Number:
        '''(experimental) The growth factor of the rollout strategy.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="finalBakeTime")
    @abc.abstractmethod
    def final_bake_time(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The final bake time of the deployment strategy.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="growthType")
    @abc.abstractmethod
    def growth_type(self) -> typing.Optional[GrowthType]:
        '''(experimental) The growth type of the rollout strategy.

        :stability: experimental
        '''
        ...


class _RolloutStrategyProxy(RolloutStrategy):
    @builtins.property
    @jsii.member(jsii_name="deploymentDuration")
    def deployment_duration(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The deployment duration of the rollout strategy.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Duration, jsii.get(self, "deploymentDuration"))

    @builtins.property
    @jsii.member(jsii_name="growthFactor")
    def growth_factor(self) -> jsii.Number:
        '''(experimental) The growth factor of the rollout strategy.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "growthFactor"))

    @builtins.property
    @jsii.member(jsii_name="finalBakeTime")
    def final_bake_time(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The final bake time of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "finalBakeTime"))

    @builtins.property
    @jsii.member(jsii_name="growthType")
    def growth_type(self) -> typing.Optional[GrowthType]:
        '''(experimental) The growth type of the rollout strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[GrowthType], jsii.get(self, "growthType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, RolloutStrategy).__jsii_proxy_class__ = lambda : _RolloutStrategyProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.RolloutStrategyProps",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_duration": "deploymentDuration",
        "growth_factor": "growthFactor",
        "final_bake_time": "finalBakeTime",
    },
)
class RolloutStrategyProps:
    def __init__(
        self,
        *,
        deployment_duration: _aws_cdk_ceddda9d.Duration,
        growth_factor: jsii.Number,
        final_bake_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Properties for the Rollout Strategy.

        :param deployment_duration: (experimental) The deployment duration of the deployment strategy. This defines the total amount of time for a deployment to last.
        :param growth_factor: (experimental) The growth factor of the deployment strategy. This defines the percentage of targets to receive a deployed configuration during each interval.
        :param final_bake_time: (experimental) The final bake time of the deployment strategy. This setting specifies the amount of time AWS AppConfig monitors for Amazon CloudWatch alarms after the configuration has been deployed to 100% of its targets, before considering the deployment to be complete. If an alarm is triggered during this time, AWS AppConfig rolls back the deployment. Default: Duration.minutes(0)

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # application: appconfig.Application
            
            
            appconfig.HostedConfiguration(self, "MyHostedConfiguration",
                application=application,
                content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
                deployment_strategy=appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
                    rollout_strategy=appconfig.RolloutStrategy.linear(
                        growth_factor=15,
                        deployment_duration=Duration.minutes(30),
                        final_bake_time=Duration.minutes(15)
                    )
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__025fe43cb0975a69395526e43ec36d0ea67b5df69c3fe3d207acddf2ac6132bb)
            check_type(argname="argument deployment_duration", value=deployment_duration, expected_type=type_hints["deployment_duration"])
            check_type(argname="argument growth_factor", value=growth_factor, expected_type=type_hints["growth_factor"])
            check_type(argname="argument final_bake_time", value=final_bake_time, expected_type=type_hints["final_bake_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "deployment_duration": deployment_duration,
            "growth_factor": growth_factor,
        }
        if final_bake_time is not None:
            self._values["final_bake_time"] = final_bake_time

    @builtins.property
    def deployment_duration(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The deployment duration of the deployment strategy.

        This defines
        the total amount of time for a deployment to last.

        :stability: experimental
        '''
        result = self._values.get("deployment_duration")
        assert result is not None, "Required property 'deployment_duration' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    @builtins.property
    def growth_factor(self) -> jsii.Number:
        '''(experimental) The growth factor of the deployment strategy.

        This defines
        the percentage of targets to receive a deployed configuration
        during each interval.

        :stability: experimental
        '''
        result = self._values.get("growth_factor")
        assert result is not None, "Required property 'growth_factor' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def final_bake_time(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The final bake time of the deployment strategy.

        This setting specifies the amount of time AWS AppConfig monitors for Amazon
        CloudWatch alarms after the configuration has been deployed to
        100% of its targets, before considering the deployment to be complete.
        If an alarm is triggered during this time, AWS AppConfig rolls back
        the deployment.

        :default: Duration.minutes(0)

        :stability: experimental
        '''
        result = self._values.get("final_bake_time")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RolloutStrategyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IEventDestination)
class SnsDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.SnsDestination",
):
    '''(experimental) Use an Amazon SNS topic as an event destination.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # topic: sns.Topic
        
        
        appconfig.Extension(self, "MyExtension",
            actions=[
                appconfig.Action(
                    action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                    event_destination=appconfig.SnsDestination(topic)
                )
            ]
        )
    '''

    def __init__(self, topic: _aws_cdk_aws_sns_ceddda9d.ITopic) -> None:
        '''
        :param topic: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dbf8f0560e66b03f398512b32c28e80f7e3004dadcf35a0fe8ea6c5aa6f8559)
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
        jsii.create(self.__class__, self, [topic])

    @builtins.property
    @jsii.member(jsii_name="extensionUri")
    def extension_uri(self) -> builtins.str:
        '''(experimental) The URI of the extension event destination.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionUri"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceType":
        '''(experimental) The type of the extension event destination.

        :stability: experimental
        '''
        return typing.cast("SourceType", jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="policyDocument")
    def policy_document(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) The IAM policy document to invoke the event destination.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], jsii.get(self, "policyDocument"))


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.SourceType")
class SourceType(enum.Enum):
    '''(experimental) Defines the source type for event destinations.

    :stability: experimental
    '''

    LAMBDA = "LAMBDA"
    '''
    :stability: experimental
    '''
    SQS = "SQS"
    '''
    :stability: experimental
    '''
    SNS = "SNS"
    '''
    :stability: experimental
    '''
    EVENTS = "EVENTS"
    '''
    :stability: experimental
    '''


@jsii.implements(IConfiguration, IExtensible)
class SourcedConfiguration(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.SourcedConfiguration",
):
    '''(experimental) A sourced configuration represents configuration stored in an Amazon S3 bucket, AWS Secrets Manager secret, Systems Manager (SSM) Parameter Store parameter, SSM document, or AWS CodePipeline.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        # bucket: s3.Bucket
        
        
        appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
            application=application,
            location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
            type=appconfig.ConfigurationType.FEATURE_FLAGS,
            name="MyConfig",
            description="This is my sourced configuration from CDK."
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        location: ConfigurationSource,
        retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        version_number: typing.Optional[builtins.str] = None,
        application: IApplication,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
        deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence[IValidator]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param location: (experimental) The location where the configuration is stored.
        :param retrieval_role: (experimental) The IAM role to retrieve the configuration. Default: - A role is generated.
        :param version_number: (experimental) The version number of the sourced configuration to deploy. If this is not specified, then there will be no deployment. Default: - None.
        :param application: (experimental) The application associated with the configuration.
        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6de714e75d8600c9c89bf472f703f1133c657cc4643d601a27a57d45f26d39c1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SourcedConfigurationProps(
            location=location,
            retrieval_role=retrieval_role,
            version_number=version_number,
            application=application,
            deployment_key=deployment_key,
            deployment_strategy=deployment_strategy,
            deploy_to=deploy_to,
            description=description,
            name=name,
            type=type,
            validators=validators,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addExistingEnvironmentsToApplication")
    def _add_existing_environments_to_application(self) -> None:
        '''
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addExistingEnvironmentsToApplication", []))

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: IExtension) -> None:
        '''(experimental) Adds an extension association to the configuration profile.

        :param extension: The extension to create an association for.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e36a51e8c648a38e29e6d73c8d4c8347ef47d01e396d0992ad696e3909d836b0)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
        return typing.cast(None, jsii.invoke(self, "addExtension", [extension]))

    @jsii.member(jsii_name="deploy")
    def deploy(self, environment: IEnvironment) -> None:
        '''(experimental) Deploys the configuration to the specified environment.

        :param environment: The environment to deploy the configuration to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b274b1b9b259cab832bccebd6f919f795a9ba1c88fe25b7c5f9e2d00dd5a93e7)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
        return typing.cast(None, jsii.invoke(self, "deploy", [environment]))

    @jsii.member(jsii_name="deployConfigToEnvironments")
    def _deploy_config_to_environments(self) -> None:
        '''
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "deployConfigToEnvironments", []))

    @jsii.member(jsii_name="getDeploymentHash")
    def _get_deployment_hash(self, environment: IEnvironment) -> builtins.str:
        '''
        :param environment: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a293d829ce6a01342f729da0737185357eed648d3de40bf4d7afb8371ffbc2af)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
        return typing.cast(builtins.str, jsii.invoke(self, "getDeploymentHash", [environment]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to the configuration profile.

        :param action_point: The action point which triggers the event.
        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc0a24473ea37ab3e38e04a2b7e35d326a2022cb2a6873667bff9f09a2ee7c50)
            check_type(argname="argument action_point", value=action_point, expected_type=type_hints["action_point"])
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "on", [action_point, event_destination, options]))

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaebe88fe39bec5c306c39a0383eb089d4e6d7fff898f2e37b7386e9fcced05c)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentBaking", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__683f88c78f824b0a1d4a7c04f266c989dfe304d2c6ede7824de0e4e83c9627f5)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentComplete", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5405a720615a315d4b718843047972bb3bfbc2e09f09c95bb75a3117418581d5)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentRolledBack", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb144853ce53c005604325fe0e7ac87ddcaada3557c25ef8ce5986f30098d5fc)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStart", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5c5f1baed64ed28254e6abb76f287d860e8a2f1420e1577c4e527a75d148d19)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStep", [event_destination, options]))

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8562a293ac9c2dc7b084d227cbc2c9170492f5c9b71c951e447838c3ba559234)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preCreateHostedConfigurationVersion", [event_destination, options]))

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23c6f7b3bc4d81ae08d5f43d800b223b91c7c521da585eb64149372d7f374430)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preStartDeployment", [event_destination, options]))

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> IApplication:
        '''(experimental) The application associated with the configuration.

        :stability: experimental
        '''
        return typing.cast(IApplication, jsii.get(self, "application"))

    @builtins.property
    @jsii.member(jsii_name="configurationProfileArn")
    def configuration_profile_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the configuration profile.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "configurationProfileArn"))

    @builtins.property
    @jsii.member(jsii_name="configurationProfileId")
    def configuration_profile_id(self) -> builtins.str:
        '''(experimental) The ID of the configuration profile.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "configurationProfileId"))

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> ConfigurationSource:
        '''(experimental) The location where the configuration is stored.

        :stability: experimental
        '''
        return typing.cast(ConfigurationSource, jsii.get(self, "location"))

    @builtins.property
    @jsii.member(jsii_name="deploymentKey")
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "deploymentKey"))

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategy")
    def deployment_strategy(self) -> typing.Optional[IDeploymentStrategy]:
        '''(experimental) The deployment strategy for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IDeploymentStrategy], jsii.get(self, "deploymentStrategy"))

    @builtins.property
    @jsii.member(jsii_name="deployTo")
    def deploy_to(self) -> typing.Optional[typing.List[IEnvironment]]:
        '''(experimental) The environments to deploy to.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[IEnvironment]], jsii.get(self, "deployTo"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="retrievalRole")
    def retrieval_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role to retrieve the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "retrievalRole"))

    @builtins.property
    @jsii.member(jsii_name="sourceKey")
    def source_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The key to decrypt the configuration if applicable.

        This key
        can be used when storing configuration in AWS Secrets Manager, Systems Manager Parameter Store,
        or Amazon S3.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "sourceKey"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[ConfigurationType]:
        '''(experimental) The configuration type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ConfigurationType], jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="validators")
    def validators(self) -> typing.Optional[typing.List[IValidator]]:
        '''(experimental) The validators for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[IValidator]], jsii.get(self, "validators"))

    @builtins.property
    @jsii.member(jsii_name="versionNumber")
    def version_number(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version number of the configuration to deploy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionNumber"))

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def _application_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @_application_id.setter
    def _application_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce9e31769f81508dd6b0016c290f7a63a8cf622d23b1acfe37cde862df190c9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationId", value)

    @builtins.property
    @jsii.member(jsii_name="extensible")
    def _extensible(self) -> "ExtensibleBase":
        '''
        :stability: experimental
        '''
        return typing.cast("ExtensibleBase", jsii.get(self, "extensible"))

    @_extensible.setter
    def _extensible(self, value: "ExtensibleBase") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__880e151905363813bdf526a88d4d06eb5335ace3d63b330df7c16bb70c59f469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extensible", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.SourcedConfigurationOptions",
    jsii_struct_bases=[ConfigurationOptions],
    name_mapping={
        "deployment_key": "deploymentKey",
        "deployment_strategy": "deploymentStrategy",
        "deploy_to": "deployTo",
        "description": "description",
        "name": "name",
        "type": "type",
        "validators": "validators",
        "location": "location",
        "retrieval_role": "retrievalRole",
        "version_number": "versionNumber",
    },
)
class SourcedConfigurationOptions(ConfigurationOptions):
    def __init__(
        self,
        *,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
        deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence[IValidator]] = None,
        location: ConfigurationSource,
        retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        version_number: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for SourcedConfiguration.

        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.
        :param location: (experimental) The location where the configuration is stored.
        :param retrieval_role: (experimental) The IAM role to retrieve the configuration. Default: - A role is generated.
        :param version_number: (experimental) The version number of the sourced configuration to deploy. If this is not specified, then there will be no deployment. Default: - None.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appconfig_alpha as appconfig_alpha
            from aws_cdk import aws_iam as iam
            from aws_cdk import aws_kms as kms
            
            # configuration_source: appconfig_alpha.ConfigurationSource
            # deployment_strategy: appconfig_alpha.DeploymentStrategy
            # environment: appconfig_alpha.Environment
            # key: kms.Key
            # role: iam.Role
            # validator: appconfig_alpha.IValidator
            
            sourced_configuration_options = appconfig_alpha.SourcedConfigurationOptions(
                location=configuration_source,
            
                # the properties below are optional
                deployment_key=key,
                deployment_strategy=deployment_strategy,
                deploy_to=[environment],
                description="description",
                name="name",
                retrieval_role=role,
                type=appconfig_alpha.ConfigurationType.FREEFORM,
                validators=[validator],
                version_number="versionNumber"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9492a8feb2804ba1165784df24ecde57a1e3e180f9074add9b343bd5782d9d5b)
            check_type(argname="argument deployment_key", value=deployment_key, expected_type=type_hints["deployment_key"])
            check_type(argname="argument deployment_strategy", value=deployment_strategy, expected_type=type_hints["deployment_strategy"])
            check_type(argname="argument deploy_to", value=deploy_to, expected_type=type_hints["deploy_to"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument validators", value=validators, expected_type=type_hints["validators"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument retrieval_role", value=retrieval_role, expected_type=type_hints["retrieval_role"])
            check_type(argname="argument version_number", value=version_number, expected_type=type_hints["version_number"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "location": location,
        }
        if deployment_key is not None:
            self._values["deployment_key"] = deployment_key
        if deployment_strategy is not None:
            self._values["deployment_strategy"] = deployment_strategy
        if deploy_to is not None:
            self._values["deploy_to"] = deploy_to
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type
        if validators is not None:
            self._values["validators"] = validators
        if retrieval_role is not None:
            self._values["retrieval_role"] = retrieval_role
        if version_number is not None:
            self._values["version_number"] = version_number

    @builtins.property
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key of the configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deployment_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def deployment_strategy(self) -> typing.Optional[IDeploymentStrategy]:
        '''(experimental) The deployment strategy for the configuration.

        :default:

        - A deployment strategy with the rollout strategy set to
        RolloutStrategy.CANARY_10_PERCENT_20_MINUTES

        :stability: experimental
        '''
        result = self._values.get("deployment_strategy")
        return typing.cast(typing.Optional[IDeploymentStrategy], result)

    @builtins.property
    def deploy_to(self) -> typing.Optional[typing.List[IEnvironment]]:
        '''(experimental) The list of environments to deploy the configuration to.

        If this parameter is not specified, then there will be no
        deployment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deploy_to")
        return typing.cast(typing.Optional[typing.List[IEnvironment]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[ConfigurationType]:
        '''(experimental) The type of configuration.

        :default: ConfigurationType.FREEFORM

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[ConfigurationType], result)

    @builtins.property
    def validators(self) -> typing.Optional[typing.List[IValidator]]:
        '''(experimental) The validators for the configuration.

        :default: - No validators.

        :stability: experimental
        '''
        result = self._values.get("validators")
        return typing.cast(typing.Optional[typing.List[IValidator]], result)

    @builtins.property
    def location(self) -> ConfigurationSource:
        '''(experimental) The location where the configuration is stored.

        :stability: experimental
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(ConfigurationSource, result)

    @builtins.property
    def retrieval_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role to retrieve the configuration.

        :default: - A role is generated.

        :stability: experimental
        '''
        result = self._values.get("retrieval_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def version_number(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version number of the sourced configuration to deploy.

        If this is not specified,
        then there will be no deployment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("version_number")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SourcedConfigurationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appconfig-alpha.SourcedConfigurationProps",
    jsii_struct_bases=[ConfigurationProps],
    name_mapping={
        "deployment_key": "deploymentKey",
        "deployment_strategy": "deploymentStrategy",
        "deploy_to": "deployTo",
        "description": "description",
        "name": "name",
        "type": "type",
        "validators": "validators",
        "application": "application",
        "location": "location",
        "retrieval_role": "retrievalRole",
        "version_number": "versionNumber",
    },
)
class SourcedConfigurationProps(ConfigurationProps):
    def __init__(
        self,
        *,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
        deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence[IValidator]] = None,
        application: IApplication,
        location: ConfigurationSource,
        retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        version_number: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for SourcedConfiguration.

        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.
        :param application: (experimental) The application associated with the configuration.
        :param location: (experimental) The location where the configuration is stored.
        :param retrieval_role: (experimental) The IAM role to retrieve the configuration. Default: - A role is generated.
        :param version_number: (experimental) The version number of the sourced configuration to deploy. If this is not specified, then there will be no deployment. Default: - None.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # application: appconfig.Application
            # bucket: s3.Bucket
            
            
            appconfig.SourcedConfiguration(self, "MySourcedConfiguration",
                application=application,
                location=appconfig.ConfigurationSource.from_bucket(bucket, "path/to/file.json"),
                type=appconfig.ConfigurationType.FEATURE_FLAGS,
                name="MyConfig",
                description="This is my sourced configuration from CDK."
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daa8791acb6ccb376933d3df473b581618cf6594e46748b37acd98a5e40a0f9c)
            check_type(argname="argument deployment_key", value=deployment_key, expected_type=type_hints["deployment_key"])
            check_type(argname="argument deployment_strategy", value=deployment_strategy, expected_type=type_hints["deployment_strategy"])
            check_type(argname="argument deploy_to", value=deploy_to, expected_type=type_hints["deploy_to"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument validators", value=validators, expected_type=type_hints["validators"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument retrieval_role", value=retrieval_role, expected_type=type_hints["retrieval_role"])
            check_type(argname="argument version_number", value=version_number, expected_type=type_hints["version_number"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application": application,
            "location": location,
        }
        if deployment_key is not None:
            self._values["deployment_key"] = deployment_key
        if deployment_strategy is not None:
            self._values["deployment_strategy"] = deployment_strategy
        if deploy_to is not None:
            self._values["deploy_to"] = deploy_to
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type
        if validators is not None:
            self._values["validators"] = validators
        if retrieval_role is not None:
            self._values["retrieval_role"] = retrieval_role
        if version_number is not None:
            self._values["version_number"] = version_number

    @builtins.property
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key of the configuration.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deployment_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def deployment_strategy(self) -> typing.Optional[IDeploymentStrategy]:
        '''(experimental) The deployment strategy for the configuration.

        :default:

        - A deployment strategy with the rollout strategy set to
        RolloutStrategy.CANARY_10_PERCENT_20_MINUTES

        :stability: experimental
        '''
        result = self._values.get("deployment_strategy")
        return typing.cast(typing.Optional[IDeploymentStrategy], result)

    @builtins.property
    def deploy_to(self) -> typing.Optional[typing.List[IEnvironment]]:
        '''(experimental) The list of environments to deploy the configuration to.

        If this parameter is not specified, then there will be no
        deployment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("deploy_to")
        return typing.cast(typing.Optional[typing.List[IEnvironment]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :default: - No description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :default: - A name is generated.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[ConfigurationType]:
        '''(experimental) The type of configuration.

        :default: ConfigurationType.FREEFORM

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[ConfigurationType], result)

    @builtins.property
    def validators(self) -> typing.Optional[typing.List[IValidator]]:
        '''(experimental) The validators for the configuration.

        :default: - No validators.

        :stability: experimental
        '''
        result = self._values.get("validators")
        return typing.cast(typing.Optional[typing.List[IValidator]], result)

    @builtins.property
    def application(self) -> IApplication:
        '''(experimental) The application associated with the configuration.

        :stability: experimental
        '''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast(IApplication, result)

    @builtins.property
    def location(self) -> ConfigurationSource:
        '''(experimental) The location where the configuration is stored.

        :stability: experimental
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(ConfigurationSource, result)

    @builtins.property
    def retrieval_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role to retrieve the configuration.

        :default: - A role is generated.

        :stability: experimental
        '''
        result = self._values.get("retrieval_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def version_number(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version number of the sourced configuration to deploy.

        If this is not specified,
        then there will be no deployment.

        :default: - None.

        :stability: experimental
        '''
        result = self._values.get("version_number")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SourcedConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IEventDestination)
class SqsDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.SqsDestination",
):
    '''(experimental) Use an Amazon SQS queue as an event destination.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # queue: sqs.Queue
        
        
        appconfig.Extension(self, "MyExtension",
            actions=[
                appconfig.Action(
                    action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                    event_destination=appconfig.SqsDestination(queue)
                )
            ]
        )
    '''

    def __init__(self, queue: _aws_cdk_aws_sqs_ceddda9d.IQueue) -> None:
        '''
        :param queue: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98bb01edb9242ee60f63e0f0dcb21cd2dbebf540de603c1c71b2b4f16e8079c)
            check_type(argname="argument queue", value=queue, expected_type=type_hints["queue"])
        jsii.create(self.__class__, self, [queue])

    @builtins.property
    @jsii.member(jsii_name="extensionUri")
    def extension_uri(self) -> builtins.str:
        '''(experimental) The URI of the extension event destination.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionUri"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> SourceType:
        '''(experimental) The type of the extension event destination.

        :stability: experimental
        '''
        return typing.cast(SourceType, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="policyDocument")
    def policy_document(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) The IAM policy document to invoke the event destination.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], jsii.get(self, "policyDocument"))


@jsii.enum(jsii_type="@aws-cdk/aws-appconfig-alpha.ValidatorType")
class ValidatorType(enum.Enum):
    '''(experimental) The validator type.

    :stability: experimental
    '''

    JSON_SCHEMA = "JSON_SCHEMA"
    '''(experimental) JSON Scema validator.

    :stability: experimental
    '''
    LAMBDA = "LAMBDA"
    '''(experimental) Validate using a Lambda function.

    :stability: experimental
    '''


@jsii.implements(IApplication, IExtensible)
class Application(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.Application",
):
    '''(experimental) An AWS AppConfig application.

    :see: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-application.html
    :stability: experimental
    :resource: AWS::AppConfig::Application
    :exampleMetadata: infused

    Example::

        appconfig.Application(self, "MyApplication")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: (experimental) The description for the application. Default: - No description.
        :param name: (experimental) The name of the application. Default: - A name is generated.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c06278bbcf84f572ef3db3450783b06a4b0f6271579004cba1c0e313661b0db)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApplicationProps(description=description, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAgentToEcs")
    @builtins.classmethod
    def add_agent_to_ecs(
        cls,
        task_def: _aws_cdk_aws_ecs_ceddda9d.TaskDefinition,
    ) -> None:
        '''(experimental) Adds the AWS AppConfig Agent as a container to the provided ECS task definition.

        :param task_def: The ECS task definition.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9caa944ae8798e28582f33374dd627a3cbd66962bb9a550e674619684f7bd041)
            check_type(argname="argument task_def", value=task_def, expected_type=type_hints["task_def"])
        return typing.cast(None, jsii.sinvoke(cls, "addAgentToEcs", [task_def]))

    @jsii.member(jsii_name="fromApplicationArn")
    @builtins.classmethod
    def from_application_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        application_arn: builtins.str,
    ) -> IApplication:
        '''(experimental) Imports an AWS AppConfig application into the CDK using its Amazon Resource Name (ARN).

        :param scope: The parent construct.
        :param id: The name of the application construct.
        :param application_arn: The Amazon Resource Name (ARN) of the application.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68b9f8dc9f5f8c80cdb7992113df780ea1a4262b334fd5effbe1daebf13637df)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument application_arn", value=application_arn, expected_type=type_hints["application_arn"])
        return typing.cast(IApplication, jsii.sinvoke(cls, "fromApplicationArn", [scope, id, application_arn]))

    @jsii.member(jsii_name="fromApplicationId")
    @builtins.classmethod
    def from_application_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        application_id: builtins.str,
    ) -> IApplication:
        '''(experimental) Imports an AWS AppConfig application into the CDK using its ID.

        :param scope: The parent construct.
        :param id: The name of the application construct.
        :param application_id: The ID of the application.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c041dd17777e5fb65364b4f88f6d759aea2766749b647c8b8c035c0912eb435)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument application_id", value=application_id, expected_type=type_hints["application_id"])
        return typing.cast(IApplication, jsii.sinvoke(cls, "fromApplicationId", [scope, id, application_id]))

    @jsii.member(jsii_name="getLambdaLayerVersionArn")
    @builtins.classmethod
    def get_lambda_layer_version_arn(
        cls,
        region: builtins.str,
        platform: typing.Optional[Platform] = None,
    ) -> builtins.str:
        '''(experimental) Retrieves the Lambda layer version Amazon Resource Name (ARN) for the AWS AppConfig Lambda extension.

        :param region: The region for the Lambda layer (for example, 'us-east-1').
        :param platform: The platform for the Lambda layer (default is Platform.X86_64).

        :return: Lambda layer version ARN

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f7eef57e3a7fc00af57036e1382b0a999ff5a680968dc37347d5ff7ce0709ba)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument platform", value=platform, expected_type=type_hints["platform"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "getLambdaLayerVersionArn", [region, platform]))

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        monitors: typing.Optional[typing.Sequence[Monitor]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> IEnvironment:
        '''(experimental) Adds an environment.

        :param id: -
        :param description: (experimental) The description of the environment. Default: - No description.
        :param monitors: (experimental) The monitors for the environment. Default: - No monitors.
        :param name: (experimental) The name of the environment. Default: - A name is generated.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb35f92bfd5eecbafe942d09fb3c8690d18dd2faded276b8ad47c061da1f01cb)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = EnvironmentOptions(
            description=description, monitors=monitors, name=name
        )

        return typing.cast(IEnvironment, jsii.invoke(self, "addEnvironment", [id, options]))

    @jsii.member(jsii_name="addExistingEnvironment")
    def add_existing_environment(self, environment: IEnvironment) -> None:
        '''(experimental) Adds an existing environment.

        :param environment: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1ae8660aa0ae59983dcae4d90d353b11f142207782e84351053777bf812d055)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
        return typing.cast(None, jsii.invoke(self, "addExistingEnvironment", [environment]))

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: IExtension) -> None:
        '''(experimental) Adds an extension association to the application.

        :param extension: The extension to create an association for.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5546e5506fa4132fb9f95d3b1cd936c6f9546651f3aec84e804375c99179ab07)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
        return typing.cast(None, jsii.invoke(self, "addExtension", [extension]))

    @jsii.member(jsii_name="addHostedConfiguration")
    def add_hosted_configuration(
        self,
        id: builtins.str,
        *,
        content: ConfigurationContent,
        latest_version_number: typing.Optional[jsii.Number] = None,
        version_label: typing.Optional[builtins.str] = None,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
        deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence[IValidator]] = None,
    ) -> "HostedConfiguration":
        '''(experimental) Adds a hosted configuration.

        :param id: -
        :param content: (experimental) The content of the hosted configuration.
        :param latest_version_number: (experimental) The latest version number of the hosted configuration. Default: - None.
        :param version_label: (experimental) The version label of the hosted configuration. Default: - None.
        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__234b26cc7cba220095235318be07f117ab450275fcf95be76c527dc79d8cbfeb)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = HostedConfigurationOptions(
            content=content,
            latest_version_number=latest_version_number,
            version_label=version_label,
            deployment_key=deployment_key,
            deployment_strategy=deployment_strategy,
            deploy_to=deploy_to,
            description=description,
            name=name,
            type=type,
            validators=validators,
        )

        return typing.cast("HostedConfiguration", jsii.invoke(self, "addHostedConfiguration", [id, options]))

    @jsii.member(jsii_name="addSourcedConfiguration")
    def add_sourced_configuration(
        self,
        id: builtins.str,
        *,
        location: ConfigurationSource,
        retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        version_number: typing.Optional[builtins.str] = None,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
        deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence[IValidator]] = None,
    ) -> SourcedConfiguration:
        '''(experimental) Adds a sourced configuration.

        :param id: -
        :param location: (experimental) The location where the configuration is stored.
        :param retrieval_role: (experimental) The IAM role to retrieve the configuration. Default: - A role is generated.
        :param version_number: (experimental) The version number of the sourced configuration to deploy. If this is not specified, then there will be no deployment. Default: - None.
        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d60d9b18c9f5504c609a0d3ddcb2cdd95361b4160a766a7d973c38ffb81812d8)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = SourcedConfigurationOptions(
            location=location,
            retrieval_role=retrieval_role,
            version_number=version_number,
            deployment_key=deployment_key,
            deployment_strategy=deployment_strategy,
            deploy_to=deploy_to,
            description=description,
            name=name,
            type=type,
            validators=validators,
        )

        return typing.cast(SourcedConfiguration, jsii.invoke(self, "addSourcedConfiguration", [id, options]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to an application.

        :param action_point: The action point which triggers the event.
        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14083b415432d04d7b2f4fd1f5ac7f652a696d1e230f43a0a6fd831cf766a8ed)
            check_type(argname="argument action_point", value=action_point, expected_type=type_hints["action_point"])
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "on", [action_point, event_destination, options]))

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to an application.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25a75086843710b75031132295de45c22017935502bb8be809f5d65a28373203)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentBaking", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to an application.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c058feaa5b07af2b3dd4de3f791c3b39c354cf6a242997b3aa54e2d7346e1f7)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentComplete", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to an application.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e36a1db3e27d21dbd66ddc43ea918e4c0d6e096b27c165b3e5383fa49031352)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentRolledBack", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to an application.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cd4e324f7e421e1efd6db1c675383e581fcf209b03c9023d58d27862c3a8c03)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStart", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to an application.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__102b08c8649225f48ed05c41c8306c0b6ff96ca478b39431ee26ecdfd7e5670c)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStep", [event_destination, options]))

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to an application.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acaed06c24f5efcae747fa3085b567c71ea9657915630d49e2f5563c0be96a1c)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preCreateHostedConfigurationVersion", [event_destination, options]))

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to an application.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be4c900b86e39cd9f74ed235d5d2a634a437d5d2d0eec99555c3af996b92c74f)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preStartDeployment", [event_destination, options]))

    @builtins.property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property
    @jsii.member(jsii_name="environments")
    def environments(self) -> typing.List[IEnvironment]:
        '''(experimental) Returns the list of associated environments.

        :stability: experimental
        '''
        return typing.cast(typing.List[IEnvironment], jsii.get(self, "environments"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the application.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the application.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="extensible")
    def _extensible(self) -> "ExtensibleBase":
        '''
        :stability: experimental
        '''
        return typing.cast("ExtensibleBase", jsii.get(self, "extensible"))

    @_extensible.setter
    def _extensible(self, value: "ExtensibleBase") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3d7bb051f73db36d08c21912a98b4301b3736c7c90696b529618c8b01c8c784)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extensible", value)


@jsii.implements(IDeploymentStrategy)
class DeploymentStrategy(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.DeploymentStrategy",
):
    '''(experimental) An AWS AppConfig deployment strategy.

    :see: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html
    :stability: experimental
    :resource: AWS::AppConfig::DeploymentStrategy
    :exampleMetadata: infused

    Example::

        appconfig.DeploymentStrategy(self, "MyDeploymentStrategy",
            rollout_strategy=appconfig.RolloutStrategy.linear(
                growth_factor=20,
                deployment_duration=Duration.minutes(30),
                final_bake_time=Duration.minutes(30)
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        rollout_strategy: RolloutStrategy,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param rollout_strategy: (experimental) The rollout strategy for the deployment strategy. You can use predefined deployment strategies, such as RolloutStrategy.ALL_AT_ONCE, RolloutStrategy.LINEAR_50_PERCENT_EVERY_30_SECONDS, or RolloutStrategy.CANARY_10_PERCENT_20_MINUTES.
        :param description: (experimental) A description of the deployment strategy. Default: - No description.
        :param name: (experimental) A name for the deployment strategy. Default: - A name is generated.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5ac3fe993db44abd9a7f73f407703f2374964efab918c870dc032e803b98870)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DeploymentStrategyProps(
            rollout_strategy=rollout_strategy, description=description, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromDeploymentStrategyArn")
    @builtins.classmethod
    def from_deployment_strategy_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        deployment_strategy_arn: builtins.str,
    ) -> IDeploymentStrategy:
        '''(experimental) Imports a deployment strategy into the CDK using its Amazon Resource Name (ARN).

        :param scope: The parent construct.
        :param id: The name of the deployment strategy construct.
        :param deployment_strategy_arn: The Amazon Resource Name (ARN) of the deployment strategy.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f07353181054ceb0eb73b166aa63e7d6196f4c2c7140dd380b6e9ac76684122)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument deployment_strategy_arn", value=deployment_strategy_arn, expected_type=type_hints["deployment_strategy_arn"])
        return typing.cast(IDeploymentStrategy, jsii.sinvoke(cls, "fromDeploymentStrategyArn", [scope, id, deployment_strategy_arn]))

    @jsii.member(jsii_name="fromDeploymentStrategyId")
    @builtins.classmethod
    def from_deployment_strategy_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        deployment_strategy_id: builtins.str,
    ) -> IDeploymentStrategy:
        '''(experimental) Imports a deployment strategy into the CDK using its ID.

        :param scope: The parent construct.
        :param id: The name of the deployment strategy construct.
        :param deployment_strategy_id: The ID of the deployment strategy.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b9cc49e5afdc0c3b1859567b3c803a18d47ff6ea27bc9b1361d65c136a0396)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument deployment_strategy_id", value=deployment_strategy_id, expected_type=type_hints["deployment_strategy_id"])
        return typing.cast(IDeploymentStrategy, jsii.sinvoke(cls, "fromDeploymentStrategyId", [scope, id, deployment_strategy_id]))

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategyArn")
    def deployment_strategy_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the deployment strategy.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "deploymentStrategyArn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategyId")
    def deployment_strategy_id(self) -> builtins.str:
        '''(experimental) The ID of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deploymentStrategyId"))

    @builtins.property
    @jsii.member(jsii_name="deploymentDurationInMinutes")
    def deployment_duration_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The deployment duration in minutes of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deploymentDurationInMinutes"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="finalBakeTimeInMinutes")
    def final_bake_time_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The final bake time in minutes of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "finalBakeTimeInMinutes"))

    @builtins.property
    @jsii.member(jsii_name="growthFactor")
    def growth_factor(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The growth factor of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "growthFactor"))

    @builtins.property
    @jsii.member(jsii_name="growthType")
    def growth_type(self) -> typing.Optional[GrowthType]:
        '''(experimental) The growth type of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[GrowthType], jsii.get(self, "growthType"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the deployment strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))


@jsii.implements(IEnvironment, IExtensible)
class Environment(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.Environment",
):
    '''(experimental) An AWS AppConfig environment.

    :see: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-environment.html
    :stability: experimental
    :resource: AWS::AppConfig::Environment
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        # alarm: cloudwatch.Alarm
        # composite_alarm: cloudwatch.CompositeAlarm
        
        
        appconfig.Environment(self, "MyEnvironment",
            application=application,
            monitors=[
                appconfig.Monitor.from_cloud_watch_alarm(alarm),
                appconfig.Monitor.from_cloud_watch_alarm(composite_alarm)
            ]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application: IApplication,
        description: typing.Optional[builtins.str] = None,
        monitors: typing.Optional[typing.Sequence[Monitor]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application: (experimental) The application to be associated with the environment.
        :param description: (experimental) The description of the environment. Default: - No description.
        :param monitors: (experimental) The monitors for the environment. Default: - No monitors.
        :param name: (experimental) The name of the environment. Default: - A name is generated.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6775ce35aca252041cd539ecac341c163f6580dfc4e3b69a6e4ca13d6d0fc107)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EnvironmentProps(
            application=application,
            description=description,
            monitors=monitors,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromEnvironmentArn")
    @builtins.classmethod
    def from_environment_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        environment_arn: builtins.str,
    ) -> IEnvironment:
        '''(experimental) Imports an environment into the CDK using its Amazon Resource Name (ARN).

        :param scope: The parent construct.
        :param id: The name of the environment construct.
        :param environment_arn: The Amazon Resource Name (ARN) of the environment.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be0a7e87fedfd9445b3657f17b5d62b82bfd9383b3f3eff442f1c8516d50a57f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument environment_arn", value=environment_arn, expected_type=type_hints["environment_arn"])
        return typing.cast(IEnvironment, jsii.sinvoke(cls, "fromEnvironmentArn", [scope, id, environment_arn]))

    @jsii.member(jsii_name="fromEnvironmentAttributes")
    @builtins.classmethod
    def from_environment_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application: IApplication,
        environment_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        monitors: typing.Optional[typing.Sequence[Monitor]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> IEnvironment:
        '''(experimental) Imports an environment into the CDK from its attributes.

        :param scope: The parent construct.
        :param id: The name of the environment construct.
        :param application: (experimental) The application associated with the environment.
        :param environment_id: (experimental) The ID of the environment.
        :param description: (experimental) The description of the environment. Default: - None.
        :param monitors: (experimental) The monitors for the environment. Default: - None.
        :param name: (experimental) The name of the environment. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce9b04126334674439c8785082064a17360e12f5130243113c51feabb9d29f09)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = EnvironmentAttributes(
            application=application,
            environment_id=environment_id,
            description=description,
            monitors=monitors,
            name=name,
        )

        return typing.cast(IEnvironment, jsii.sinvoke(cls, "fromEnvironmentAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: IExtension) -> None:
        '''(experimental) Adds an extension association to the environment.

        :param extension: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be54f9119fe91ccd509828cc845703918a09da14c25049adac3d519b95aabbbf)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
        return typing.cast(None, jsii.invoke(self, "addExtension", [extension]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to the environment.

        :param action_point: -
        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c4e89b49056050830d428a61e831383262087be9700f859e02b9c0858d5f181)
            check_type(argname="argument action_point", value=action_point, expected_type=type_hints["action_point"])
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "on", [action_point, event_destination, options]))

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b2e32567a79830faa7134d8cf4de976b9af1a888efa6a348a4d9ecf48ecb64f)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentBaking", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__818b3a1871d46350c2b2a63bcdc255c69e2606bed8874538bb8cfab2a0173f15)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentComplete", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__914b3517803f6f7b3336aa6d44584b6f3f28a8d8c0e04dbeb8990058848b95f6)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentRolledBack", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc5457eac1e0104d7f7047d43e7ba17ec5e5a103030db601df39c69e2b62ba53)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStart", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e3bd848dfa5b364d1bc2f750948cda50530fcf26a50f766c60d84402f629c25)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStep", [event_destination, options]))

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f72cdb2b7131fc110d260246dfec9e77bbeae7dad233883ae5b3d2a1fa6462e)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preCreateHostedConfigurationVersion", [event_destination, options]))

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to the environment.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18f7d2fbd9c03ffb6988f68a102b38bfba666bfe721b6e8e93823b74ed11e104)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preStartDeployment", [event_destination, options]))

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the environment.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property
    @jsii.member(jsii_name="environmentArn")
    def environment_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "environmentArn"))

    @builtins.property
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> builtins.str:
        '''(experimental) The ID of the environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "environmentId"))

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> typing.Optional[IApplication]:
        '''(experimental) The application associated with the environment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IApplication], jsii.get(self, "application"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the environment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="monitors")
    def monitors(self) -> typing.Optional[typing.List[Monitor]]:
        '''(experimental) The monitors for the environment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[Monitor]], jsii.get(self, "monitors"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the environment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="extensible")
    def _extensible(self) -> "ExtensibleBase":
        '''
        :stability: experimental
        '''
        return typing.cast("ExtensibleBase", jsii.get(self, "extensible"))

    @_extensible.setter
    def _extensible(self, value: "ExtensibleBase") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__618d32b2e68b8df805ddc1efe2f210e295699742a5b59ceb6b3eb17004b35258)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extensible", value)


@jsii.implements(IEventDestination)
class EventBridgeDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.EventBridgeDestination",
):
    '''(experimental) Use an Amazon EventBridge event bus as an event destination.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        bus = events.EventBus.from_event_bus_name(self, "MyEventBus", "default")
        
        appconfig.Extension(self, "MyExtension",
            actions=[
                appconfig.Action(
                    action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                    event_destination=appconfig.EventBridgeDestination(bus)
                )
            ]
        )
    '''

    def __init__(self, bus: _aws_cdk_aws_events_ceddda9d.IEventBus) -> None:
        '''
        :param bus: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d369243a53460e13a15e17a8fa5ce3aec7f0f665ae9ad2df0b00ad9554845ae)
            check_type(argname="argument bus", value=bus, expected_type=type_hints["bus"])
        jsii.create(self.__class__, self, [bus])

    @builtins.property
    @jsii.member(jsii_name="extensionUri")
    def extension_uri(self) -> builtins.str:
        '''(experimental) The URI of the extension event destination.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionUri"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> SourceType:
        '''(experimental) The type of the extension event destination.

        :stability: experimental
        '''
        return typing.cast(SourceType, jsii.get(self, "type"))


@jsii.implements(IExtensible)
class ExtensibleBase(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.ExtensibleBase",
):
    '''(experimental) This class is meant to be used by AWS AppConfig resources (application, configuration profile, environment) directly.

    There is currently no use
    for this class outside of the AWS AppConfig construct implementation. It is
    intended to be used with the resources since there is currently no way to
    inherit from two classes (at least within JSII constraints).

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appconfig_alpha as appconfig_alpha
        
        extensible_base = appconfig_alpha.ExtensibleBase(self, "resourceArn", "resourceName")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        resource_arn: builtins.str,
        resource_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param resource_arn: -
        :param resource_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad2873bffa0cfdcbec551cfa979c42d4399b322524961fd6adbbcdad95e88e99)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument resource_arn", value=resource_arn, expected_type=type_hints["resource_arn"])
            check_type(argname="argument resource_name", value=resource_name, expected_type=type_hints["resource_name"])
        jsii.create(self.__class__, self, [scope, resource_arn, resource_name])

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: IExtension) -> None:
        '''(experimental) Adds an extension association to the derived resource.

        :param extension: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa78143937e44300df6567c870280a7ff967c612f7663f779aff230f7d5eea47)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
        return typing.cast(None, jsii.invoke(self, "addExtension", [extension]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to the derived resource.

        :param action_point: -
        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfa7b2da79d87701fb66c30f8676abf8b75e693f9c3cecc2b951756236f2e517)
            check_type(argname="argument action_point", value=action_point, expected_type=type_hints["action_point"])
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "on", [action_point, event_destination, options]))

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__893ae21c04ab082282a4a91d53434c6bf8b7264302a91d415fd1b1511b230fad)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentBaking", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1e67d9239f5baa292365454300f5022cc65d189100adf6f1af4544c8a2d11be)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentComplete", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a33a738bc7bd64a70d02a2710dda32915943093f313e8e708ef1598e278cc31f)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentRolledBack", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3e68727572c2db9c0dcf3b7b2560bb56f6e58dfd923a08379d433cd6e28e221)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStart", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3bdb1fa02c9c6cc09af5adca3733bc2bf1215d1376aa76e3b8734ec5182d496)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStep", [event_destination, options]))

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9f798b0617c9d3a5a67da83bcf2a07731d117f481501f227e0a100301e7057c)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preCreateHostedConfigurationVersion", [event_destination, options]))

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to the derived resource.

        :param event_destination: -
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63a5d564ebf401c01446b70c7608c3f0560e657e576b517d158e40120d9ac6c8)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preStartDeployment", [event_destination, options]))


@jsii.implements(IExtension)
class Extension(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.Extension",
):
    '''(experimental) An AWS AppConfig extension.

    :see: https://docs.aws.amazon.com/appconfig/latest/userguide/working-with-appconfig-extensions.html
    :stability: experimental
    :resource: AWS::AppConfig::Extension
    :exampleMetadata: infused

    Example::

        # fn: lambda.Function
        
        
        appconfig.Extension(self, "MyExtension",
            actions=[
                appconfig.Action(
                    action_points=[appconfig.ActionPoint.ON_DEPLOYMENT_START],
                    event_destination=appconfig.LambdaDestination(fn)
                )
            ]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        actions: typing.Sequence[Action],
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param actions: (experimental) The actions for the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af8832a0d44a8fe047ed6daa99962db2e0474daef522cbc4a3baf77513e50317)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ExtensionProps(
            actions=actions,
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromExtensionArn")
    @builtins.classmethod
    def from_extension_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        extension_arn: builtins.str,
    ) -> IExtension:
        '''(experimental) Imports an extension into the CDK using its Amazon Resource Name (ARN).

        :param scope: The parent construct.
        :param id: The name of the extension construct.
        :param extension_arn: The Amazon Resource Name (ARN) of the extension.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3730d907b76b4871efdbd9c4553324fafbf6ba412680637770e2c2fba0bbb1c4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument extension_arn", value=extension_arn, expected_type=type_hints["extension_arn"])
        return typing.cast(IExtension, jsii.sinvoke(cls, "fromExtensionArn", [scope, id, extension_arn]))

    @jsii.member(jsii_name="fromExtensionAttributes")
    @builtins.classmethod
    def from_extension_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        extension_id: builtins.str,
        extension_version_number: jsii.Number,
        actions: typing.Optional[typing.Sequence[Action]] = None,
        description: typing.Optional[builtins.str] = None,
        extension_arn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> IExtension:
        '''(experimental) Imports an extension into the CDK using its attributes.

        :param scope: The parent construct.
        :param id: The name of the extension construct.
        :param extension_id: (experimental) The ID of the extension.
        :param extension_version_number: (experimental) The version number of the extension.
        :param actions: (experimental) The actions of the extension. Default: - None.
        :param description: (experimental) The description of the extension. Default: - None.
        :param extension_arn: (experimental) The Amazon Resource Name (ARN) of the extension. Default: - The extension ARN is generated.
        :param name: (experimental) The name of the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56920fdb958facebad8e5dcf817dc5c57807d47e573abf341e76418050084b35)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = ExtensionAttributes(
            extension_id=extension_id,
            extension_version_number=extension_version_number,
            actions=actions,
            description=description,
            extension_arn=extension_arn,
            name=name,
        )

        return typing.cast(IExtension, jsii.sinvoke(cls, "fromExtensionAttributes", [scope, id, attrs]))

    @builtins.property
    @jsii.member(jsii_name="extensionArn")
    def extension_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the extension.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionArn"))

    @builtins.property
    @jsii.member(jsii_name="extensionId")
    def extension_id(self) -> builtins.str:
        '''(experimental) The ID of the extension.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "extensionId"))

    @builtins.property
    @jsii.member(jsii_name="extensionVersionNumber")
    def extension_version_number(self) -> jsii.Number:
        '''(experimental) The version number of the extension.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(jsii.Number, jsii.get(self, "extensionVersionNumber"))

    @builtins.property
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.Optional[typing.List[Action]]:
        '''(experimental) The actions for the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[Action]], jsii.get(self, "actions"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionNumber")
    def latest_version_number(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The latest version number of the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "latestVersionNumber"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional[typing.List[Parameter]]:
        '''(experimental) The parameters of the extension.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[Parameter]], jsii.get(self, "parameters"))


@jsii.implements(IConfiguration, IExtensible)
class HostedConfiguration(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appconfig-alpha.HostedConfiguration",
):
    '''(experimental) A hosted configuration represents configuration stored in the AWS AppConfig hosted configuration store.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # application: appconfig.Application
        
        
        appconfig.HostedConfiguration(self, "MyHostedConfiguration",
            application=application,
            content=appconfig.ConfigurationContent.from_inline_text("This is my configuration content."),
            type=appconfig.ConfigurationType.FEATURE_FLAGS
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        content: ConfigurationContent,
        latest_version_number: typing.Optional[jsii.Number] = None,
        version_label: typing.Optional[builtins.str] = None,
        application: IApplication,
        deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
        deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ConfigurationType] = None,
        validators: typing.Optional[typing.Sequence[IValidator]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: (experimental) The content of the hosted configuration.
        :param latest_version_number: (experimental) The latest version number of the hosted configuration. Default: - None.
        :param version_label: (experimental) The version label of the hosted configuration. Default: - None.
        :param application: (experimental) The application associated with the configuration.
        :param deployment_key: (experimental) The deployment key of the configuration. Default: - None.
        :param deployment_strategy: (experimental) The deployment strategy for the configuration. Default: - A deployment strategy with the rollout strategy set to RolloutStrategy.CANARY_10_PERCENT_20_MINUTES
        :param deploy_to: (experimental) The list of environments to deploy the configuration to. If this parameter is not specified, then there will be no deployment. Default: - None.
        :param description: (experimental) The description of the configuration. Default: - No description.
        :param name: (experimental) The name of the configuration. Default: - A name is generated.
        :param type: (experimental) The type of configuration. Default: ConfigurationType.FREEFORM
        :param validators: (experimental) The validators for the configuration. Default: - No validators.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24ca4d4e414180a1e49401777ce28035f514bfbe81a2dc6f70f18a443bdac1ee)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HostedConfigurationProps(
            content=content,
            latest_version_number=latest_version_number,
            version_label=version_label,
            application=application,
            deployment_key=deployment_key,
            deployment_strategy=deployment_strategy,
            deploy_to=deploy_to,
            description=description,
            name=name,
            type=type,
            validators=validators,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addExistingEnvironmentsToApplication")
    def _add_existing_environments_to_application(self) -> None:
        '''
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addExistingEnvironmentsToApplication", []))

    @jsii.member(jsii_name="addExtension")
    def add_extension(self, extension: IExtension) -> None:
        '''(experimental) Adds an extension association to the configuration profile.

        :param extension: The extension to create an association for.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ae1a8d2f17b9ca2663d3d3a80ba0c2630d02d53b2ac862048246d5cc50a75ba)
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
        return typing.cast(None, jsii.invoke(self, "addExtension", [extension]))

    @jsii.member(jsii_name="deploy")
    def deploy(self, environment: IEnvironment) -> None:
        '''(experimental) Deploys the configuration to the specified environment.

        :param environment: The environment to deploy the configuration to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f0c2aadcb117be66617d3e087ab61602e2764c80b5eefe4b735c8ebb11aee28)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
        return typing.cast(None, jsii.invoke(self, "deploy", [environment]))

    @jsii.member(jsii_name="deployConfigToEnvironments")
    def _deploy_config_to_environments(self) -> None:
        '''
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "deployConfigToEnvironments", []))

    @jsii.member(jsii_name="getDeploymentHash")
    def _get_deployment_hash(self, environment: IEnvironment) -> builtins.str:
        '''
        :param environment: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eab02d789b656edc985af61760d9027768fe893be7a8b392f6100348f5c72b39)
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
        return typing.cast(builtins.str, jsii.invoke(self, "getDeploymentHash", [environment]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        action_point: ActionPoint,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an extension defined by the action point and event destination and also creates an extension association to the configuration profile.

        :param action_point: The action point which triggers the event.
        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__072676758a7adfd2c8fc5085433864d9cce6ad895d2edf07c92e2449ac898b17)
            check_type(argname="argument action_point", value=action_point, expected_type=type_hints["action_point"])
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "on", [action_point, event_destination, options]))

    @jsii.member(jsii_name="onDeploymentBaking")
    def on_deployment_baking(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_BAKING extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e6906904ac3ff456f9c5771351a5dbf365223e8a8af0f3c9d7e50e3dc26f9c9)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentBaking", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentComplete")
    def on_deployment_complete(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_COMPLETE extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f889c9f3bc84bcff8f6be8d33cb8864f9c53be1ab9c8966d807a1ce682b649be)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentComplete", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentRolledBack")
    def on_deployment_rolled_back(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_ROLLED_BACK extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e5bad587ed411e08e86cb527106b96fd4a99b77ddc653700d7bc4cf9b7ee095)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentRolledBack", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStart")
    def on_deployment_start(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_START extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf74da1554db8ffc9a5b9c143e702c2adbe1193e60fe1d93500399a7c125269e)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStart", [event_destination, options]))

    @jsii.member(jsii_name="onDeploymentStep")
    def on_deployment_step(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds an ON_DEPLOYMENT_STEP extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ff0d6b9be70c35693fe4f8116a81d84623bc1b55926aa61bef8e3973115607c)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "onDeploymentStep", [event_destination, options]))

    @jsii.member(jsii_name="preCreateHostedConfigurationVersion")
    def pre_create_hosted_configuration_version(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_CREATE_HOSTED_CONFIGURATION_VERSION extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f8769538eeb7d06b1c4131e60043297db26c49dca96851fc658e4a4dca603b4)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preCreateHostedConfigurationVersion", [event_destination, options]))

    @jsii.member(jsii_name="preStartDeployment")
    def pre_start_deployment(
        self,
        event_destination: IEventDestination,
        *,
        description: typing.Optional[builtins.str] = None,
        latest_version_number: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    ) -> None:
        '''(experimental) Adds a PRE_START_DEPLOYMENT extension with the provided event destination and also creates an extension association to the configuration profile.

        :param event_destination: The event that occurs during the extension.
        :param description: (experimental) A description of the extension. Default: - No description.
        :param latest_version_number: (experimental) The latest version number of the extension. When you create a new version, specify the most recent current version number. For example, you create version 3, enter 2 for this field. Default: - None.
        :param name: (experimental) The name of the extension. Default: - A name is generated.
        :param parameters: (experimental) The parameters accepted for the extension. Default: - None.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f08fe3ccf41dd427dada5be4f7948fb2bf4b0a83042d10c61987d0998aebdf3)
            check_type(argname="argument event_destination", value=event_destination, expected_type=type_hints["event_destination"])
        options = ExtensionOptions(
            description=description,
            latest_version_number=latest_version_number,
            name=name,
            parameters=parameters,
        )

        return typing.cast(None, jsii.invoke(self, "preStartDeployment", [event_destination, options]))

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> IApplication:
        '''(experimental) The application associated with the configuration.

        :stability: experimental
        '''
        return typing.cast(IApplication, jsii.get(self, "application"))

    @builtins.property
    @jsii.member(jsii_name="configurationProfileArn")
    def configuration_profile_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the configuration profile.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "configurationProfileArn"))

    @builtins.property
    @jsii.member(jsii_name="configurationProfileId")
    def configuration_profile_id(self) -> builtins.str:
        '''(experimental) The ID of the configuration profile.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "configurationProfileId"))

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        '''(experimental) The content of the hosted configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="hostedConfigurationVersionArn")
    def hosted_configuration_version_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the hosted configuration version.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "hostedConfigurationVersionArn"))

    @builtins.property
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) The content type of the hosted configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentType"))

    @builtins.property
    @jsii.member(jsii_name="deploymentKey")
    def deployment_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The deployment key for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "deploymentKey"))

    @builtins.property
    @jsii.member(jsii_name="deploymentStrategy")
    def deployment_strategy(self) -> typing.Optional[IDeploymentStrategy]:
        '''(experimental) The deployment strategy for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IDeploymentStrategy], jsii.get(self, "deploymentStrategy"))

    @builtins.property
    @jsii.member(jsii_name="deployTo")
    def deploy_to(self) -> typing.Optional[typing.List[IEnvironment]]:
        '''(experimental) The environments to deploy to.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[IEnvironment]], jsii.get(self, "deployTo"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="latestVersionNumber")
    def latest_version_number(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The latest version number of the hosted configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "latestVersionNumber"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[ConfigurationType]:
        '''(experimental) The configuration type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ConfigurationType], jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="validators")
    def validators(self) -> typing.Optional[typing.List[IValidator]]:
        '''(experimental) The validators for the configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[IValidator]], jsii.get(self, "validators"))

    @builtins.property
    @jsii.member(jsii_name="versionLabel")
    def version_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version label of the hosted configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionLabel"))

    @builtins.property
    @jsii.member(jsii_name="versionNumber")
    def version_number(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version number of the hosted configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionNumber"))

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def _application_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @_application_id.setter
    def _application_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89e23b713915e71fb90964317aefa6c4250f1bb304a477477ad7bd67d5eb1af2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationId", value)

    @builtins.property
    @jsii.member(jsii_name="extensible")
    def _extensible(self) -> ExtensibleBase:
        '''
        :stability: experimental
        '''
        return typing.cast(ExtensibleBase, jsii.get(self, "extensible"))

    @_extensible.setter
    def _extensible(self, value: ExtensibleBase) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bded0b6f2c505902525c2914f2a93aa13cb95bc7606abd473ff9f222c7540bcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extensible", value)


__all__ = [
    "Action",
    "ActionPoint",
    "ActionProps",
    "Application",
    "ApplicationProps",
    "ConfigurationContent",
    "ConfigurationOptions",
    "ConfigurationProps",
    "ConfigurationSource",
    "ConfigurationSourceType",
    "ConfigurationType",
    "DeploymentStrategy",
    "DeploymentStrategyProps",
    "Environment",
    "EnvironmentAttributes",
    "EnvironmentOptions",
    "EnvironmentProps",
    "EventBridgeDestination",
    "ExtensibleBase",
    "Extension",
    "ExtensionAttributes",
    "ExtensionOptions",
    "ExtensionProps",
    "GrowthType",
    "HostedConfiguration",
    "HostedConfigurationOptions",
    "HostedConfigurationProps",
    "IApplication",
    "IConfiguration",
    "IDeploymentStrategy",
    "IEnvironment",
    "IEventDestination",
    "IExtensible",
    "IExtension",
    "IValidator",
    "JsonSchemaValidator",
    "LambdaDestination",
    "LambdaValidator",
    "Monitor",
    "MonitorType",
    "Parameter",
    "Platform",
    "PredefinedDeploymentStrategyId",
    "RolloutStrategy",
    "RolloutStrategyProps",
    "SnsDestination",
    "SourceType",
    "SourcedConfiguration",
    "SourcedConfigurationOptions",
    "SourcedConfigurationProps",
    "SqsDestination",
    "ValidatorType",
]

publication.publish()

def _typecheckingstub__46288e96f9fe33c9bb47bbba8fb60684cbbdeea795ddf8471997b3f131bf754b(
    *,
    action_points: typing.Sequence[ActionPoint],
    event_destination: IEventDestination,
    description: typing.Optional[builtins.str] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    invoke_without_execution_role: typing.Optional[builtins.bool] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cbee3fea531afc63e09b795112d3a192860f492e731257cc8c133ed446715d8(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7502b5a45ac7c9e44b72fc76ed509700066911cda074e23bea0f68c7751951c(
    input_path: builtins.str,
    content_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__938076945a03dee347486b3ae6d3b29d530743f9051d57f0e116eb55a25f6a52(
    content: builtins.str,
    content_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b97cfe32bafabc8c80832ec71fa30bc172535bb1e5be6622f8bac4dcbece5c(
    content: builtins.str,
    content_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb192081821db66aa5a51d3f2ab560eb9f2321b2c5d128cb17fab16be4951e65(
    content: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00cade73f94a6099402ecabdf965dc4b537ad4fa7566f40836237a8715351959(
    content: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a03005065ab127f6697583f7f4ecf38e1605c1bc30404734b258b1ef55e7bef9(
    *,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27022aed1f7244394903c06489973edf6a1b616fb6a82022b7cc06e89a9d8738(
    *,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
    application: IApplication,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c136a5da041fdfb05b2c0a86bc1874615e76943e8953dfa81ca632280aeffa7(
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    object_key: builtins.str,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cb147eceae8d32d886536f36acf297c8fa3b599ea2f747071a2ee76a8015ab8(
    document: _aws_cdk_aws_ssm_ceddda9d.CfnDocument,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21c0eeb7ac9307451e9412357d4545c22ad3b112dbd04755b6832b860cb95f64(
    parameter: _aws_cdk_aws_ssm_ceddda9d.IParameter,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a7609fb6ec54ca7e1300524c441a39dc60f9d37d78666d03edd900aae96b826(
    pipeline: _aws_cdk_aws_codepipeline_ceddda9d.IPipeline,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b8f98a48c7b1026c1f2c4baaa23d27cd0483cd526e66058b6bf7efbf771c366(
    secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51e828875bce522f87198af3ef36441b4565161ebaf2b89c826ba6694eab24cb(
    *,
    rollout_strategy: RolloutStrategy,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3723a4291535d1d0cded30ff37bed9ab25f1f441461faf4960998030bb009d4b(
    *,
    application: IApplication,
    environment_id: builtins.str,
    description: typing.Optional[builtins.str] = None,
    monitors: typing.Optional[typing.Sequence[Monitor]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5140d041c3695bbfdacfa29a275e5c492198b319932b5b4f7c1355024b07fde(
    *,
    description: typing.Optional[builtins.str] = None,
    monitors: typing.Optional[typing.Sequence[Monitor]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0243b92eeec62d4462b9ebe4578a1a5cf6198a8fb56ebd9e2be61d8f4182acf(
    *,
    description: typing.Optional[builtins.str] = None,
    monitors: typing.Optional[typing.Sequence[Monitor]] = None,
    name: typing.Optional[builtins.str] = None,
    application: IApplication,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dca19bc6fb1cff56523990c90cdfc3110a0dc43adc0aa1b408b1aaedeaea231(
    *,
    extension_id: builtins.str,
    extension_version_number: jsii.Number,
    actions: typing.Optional[typing.Sequence[Action]] = None,
    description: typing.Optional[builtins.str] = None,
    extension_arn: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e06ed2a0651b17ebabdc4500ff166928dbaa8501dbbe38ef492b7e71d3664545(
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0adb87a6d8e7998dfa19a2f890b7307cc12676acbfb06dcb1c7f3f292b6c99fa(
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
    actions: typing.Sequence[Action],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32433b560156b021e78132f9bf031c8652ac89c0ca84958ebbb87deb2a83f99f(
    *,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
    content: ConfigurationContent,
    latest_version_number: typing.Optional[jsii.Number] = None,
    version_label: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae20008e7170ddf916277cfb81ca2db430b13750ea69944e998e75f56cd3fd30(
    *,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
    application: IApplication,
    content: ConfigurationContent,
    latest_version_number: typing.Optional[jsii.Number] = None,
    version_label: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ded273772482567cca9298d2ace15c1c9dbe3de9936f4295a3ea6ce23344201b(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    monitors: typing.Optional[typing.Sequence[Monitor]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1201d1bf8ee90112a8829dab2d80572c59e2f3838a2224dc3546272098827667(
    environment: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__345c530a44d22c405803db3af60a51ed00c2c2ad59a9967dba38bc40a9ce8ff5(
    id: builtins.str,
    *,
    content: ConfigurationContent,
    latest_version_number: typing.Optional[jsii.Number] = None,
    version_label: typing.Optional[builtins.str] = None,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bf4f19ff893a70198aa37f46a3fd9e0b47613dac73fc21bcd3b475b8da4d897(
    id: builtins.str,
    *,
    location: ConfigurationSource,
    retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    version_number: typing.Optional[builtins.str] = None,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ac46fdb36161e4d5ce7f88ea130c9108bd8ba6ddca74a8bedbdd2db1dcb550e(
    extension: IExtension,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb4ec93706f6de52108e02dd9f178c33d3d065b279fc305d736411bf6484289(
    action_point: ActionPoint,
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6869fb506b57d6232d5844d2d3d72dd80566b83f5fc0cf46472c31cdb7f43e93(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56fbc6fb391c8f2dd329df242cb73430a52d751b61bb18c0cfce85c56fce1bac(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e202b65f261af5d994327814052fe3be9263268a64816c79e8b00e015fd6e03(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00733fd0e9a87966284af81dc4c3bd11fa25d177801f1fcffa665792d1870beb(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__134d496601d0dded36fa012b2fdc795be5300a63d3bcf08d16f979b4d2f317e9(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebba971ad08bf09b517d3ec3c15d4a49621f4d12a780ae42b89993e02473de7b(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46989187ed1bb6e3981e270db40bf7aba6abbb31632468b1793b2896c15df51b(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b9681819f70431eaa2252ef6558d3786043224b911ed27c0d0f0db3313e95ac(
    extension: IExtension,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03324aec7fa0a3e37bb7b316301e47f73c6b1994baded6e2fdc523e922e1a62a(
    action_point: ActionPoint,
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a916f2f85ba8df6acf76806060fa9d59557b3d7bb2218dc167b4dddebdcedffe(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3e6645b7154c9953be1accc708c29fd4f4af446d189125762a1cea523c27935(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__901d296df706b6491e9e263bd0e4fa2cf3e147f336de94d840f571d9b2aec04e(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__039a5ac717b777ef278f54dbda49c2d07b1d820a53f0ea01e461a00b8a8283da(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b3421f873ed09b510fff0fe6c5fc4bbb73170ec4d6515e1ca1ac85b7ca76dda(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65d5f7d0cb5581e1244e2ddc3fdb99125fb0ee731e72a508e19463a2ddac9dca(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca95332d129113e47d1174a792d2f68a28ed1d85e195a415306a9cfd801792f0(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__136f86b4884d57f26b9d59b6da54ae94fde6312376461c60e8d858140b00d43f(
    input_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7288f476e652f7abcef985793193a15f9e580de57ebf517fd278aaafcf588742(
    code: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e734e0c6d6a359a840828087e78c1897352f2dea88a313efefab795fc5ee238(
    func: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26ae835e70fab52490538c8b8391d200a506074ceae4b3066414773817e9cd90(
    func: _aws_cdk_aws_lambda_ceddda9d.Function,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7627ea3cc658a47e724a47696800cfc227a7e24ca8ee6a99f50dab4917d2a38f(
    alarm: _aws_cdk_aws_cloudwatch_ceddda9d.IAlarm,
    alarm_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3ac48011ed8e9e256987452651269a593ca438138513a7f69f52c86a141a74e(
    name: builtins.str,
    value: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__995e35ae3e6d5944133a7f61cb3e95f1a20ef92b0e5b0a60ce4925f95b7345cf(
    name: builtins.str,
    value: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__025fe43cb0975a69395526e43ec36d0ea67b5df69c3fe3d207acddf2ac6132bb(
    *,
    deployment_duration: _aws_cdk_ceddda9d.Duration,
    growth_factor: jsii.Number,
    final_bake_time: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dbf8f0560e66b03f398512b32c28e80f7e3004dadcf35a0fe8ea6c5aa6f8559(
    topic: _aws_cdk_aws_sns_ceddda9d.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6de714e75d8600c9c89bf472f703f1133c657cc4643d601a27a57d45f26d39c1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    location: ConfigurationSource,
    retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    version_number: typing.Optional[builtins.str] = None,
    application: IApplication,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e36a51e8c648a38e29e6d73c8d4c8347ef47d01e396d0992ad696e3909d836b0(
    extension: IExtension,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b274b1b9b259cab832bccebd6f919f795a9ba1c88fe25b7c5f9e2d00dd5a93e7(
    environment: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a293d829ce6a01342f729da0737185357eed648d3de40bf4d7afb8371ffbc2af(
    environment: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc0a24473ea37ab3e38e04a2b7e35d326a2022cb2a6873667bff9f09a2ee7c50(
    action_point: ActionPoint,
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaebe88fe39bec5c306c39a0383eb089d4e6d7fff898f2e37b7386e9fcced05c(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__683f88c78f824b0a1d4a7c04f266c989dfe304d2c6ede7824de0e4e83c9627f5(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5405a720615a315d4b718843047972bb3bfbc2e09f09c95bb75a3117418581d5(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb144853ce53c005604325fe0e7ac87ddcaada3557c25ef8ce5986f30098d5fc(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5c5f1baed64ed28254e6abb76f287d860e8a2f1420e1577c4e527a75d148d19(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8562a293ac9c2dc7b084d227cbc2c9170492f5c9b71c951e447838c3ba559234(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23c6f7b3bc4d81ae08d5f43d800b223b91c7c521da585eb64149372d7f374430(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce9e31769f81508dd6b0016c290f7a63a8cf622d23b1acfe37cde862df190c9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__880e151905363813bdf526a88d4d06eb5335ace3d63b330df7c16bb70c59f469(
    value: ExtensibleBase,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9492a8feb2804ba1165784df24ecde57a1e3e180f9074add9b343bd5782d9d5b(
    *,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
    location: ConfigurationSource,
    retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    version_number: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daa8791acb6ccb376933d3df473b581618cf6594e46748b37acd98a5e40a0f9c(
    *,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
    application: IApplication,
    location: ConfigurationSource,
    retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    version_number: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98bb01edb9242ee60f63e0f0dcb21cd2dbebf540de603c1c71b2b4f16e8079c(
    queue: _aws_cdk_aws_sqs_ceddda9d.IQueue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c06278bbcf84f572ef3db3450783b06a4b0f6271579004cba1c0e313661b0db(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9caa944ae8798e28582f33374dd627a3cbd66962bb9a550e674619684f7bd041(
    task_def: _aws_cdk_aws_ecs_ceddda9d.TaskDefinition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68b9f8dc9f5f8c80cdb7992113df780ea1a4262b334fd5effbe1daebf13637df(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    application_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c041dd17777e5fb65364b4f88f6d759aea2766749b647c8b8c035c0912eb435(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    application_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f7eef57e3a7fc00af57036e1382b0a999ff5a680968dc37347d5ff7ce0709ba(
    region: builtins.str,
    platform: typing.Optional[Platform] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb35f92bfd5eecbafe942d09fb3c8690d18dd2faded276b8ad47c061da1f01cb(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    monitors: typing.Optional[typing.Sequence[Monitor]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1ae8660aa0ae59983dcae4d90d353b11f142207782e84351053777bf812d055(
    environment: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5546e5506fa4132fb9f95d3b1cd936c6f9546651f3aec84e804375c99179ab07(
    extension: IExtension,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__234b26cc7cba220095235318be07f117ab450275fcf95be76c527dc79d8cbfeb(
    id: builtins.str,
    *,
    content: ConfigurationContent,
    latest_version_number: typing.Optional[jsii.Number] = None,
    version_label: typing.Optional[builtins.str] = None,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d60d9b18c9f5504c609a0d3ddcb2cdd95361b4160a766a7d973c38ffb81812d8(
    id: builtins.str,
    *,
    location: ConfigurationSource,
    retrieval_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    version_number: typing.Optional[builtins.str] = None,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14083b415432d04d7b2f4fd1f5ac7f652a696d1e230f43a0a6fd831cf766a8ed(
    action_point: ActionPoint,
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a75086843710b75031132295de45c22017935502bb8be809f5d65a28373203(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c058feaa5b07af2b3dd4de3f791c3b39c354cf6a242997b3aa54e2d7346e1f7(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e36a1db3e27d21dbd66ddc43ea918e4c0d6e096b27c165b3e5383fa49031352(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cd4e324f7e421e1efd6db1c675383e581fcf209b03c9023d58d27862c3a8c03(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__102b08c8649225f48ed05c41c8306c0b6ff96ca478b39431ee26ecdfd7e5670c(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acaed06c24f5efcae747fa3085b567c71ea9657915630d49e2f5563c0be96a1c(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be4c900b86e39cd9f74ed235d5d2a634a437d5d2d0eec99555c3af996b92c74f(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3d7bb051f73db36d08c21912a98b4301b3736c7c90696b529618c8b01c8c784(
    value: ExtensibleBase,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5ac3fe993db44abd9a7f73f407703f2374964efab918c870dc032e803b98870(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    rollout_strategy: RolloutStrategy,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f07353181054ceb0eb73b166aa63e7d6196f4c2c7140dd380b6e9ac76684122(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    deployment_strategy_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b9cc49e5afdc0c3b1859567b3c803a18d47ff6ea27bc9b1361d65c136a0396(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    deployment_strategy_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6775ce35aca252041cd539ecac341c163f6580dfc4e3b69a6e4ca13d6d0fc107(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application: IApplication,
    description: typing.Optional[builtins.str] = None,
    monitors: typing.Optional[typing.Sequence[Monitor]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be0a7e87fedfd9445b3657f17b5d62b82bfd9383b3f3eff442f1c8516d50a57f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    environment_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce9b04126334674439c8785082064a17360e12f5130243113c51feabb9d29f09(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application: IApplication,
    environment_id: builtins.str,
    description: typing.Optional[builtins.str] = None,
    monitors: typing.Optional[typing.Sequence[Monitor]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be54f9119fe91ccd509828cc845703918a09da14c25049adac3d519b95aabbbf(
    extension: IExtension,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c4e89b49056050830d428a61e831383262087be9700f859e02b9c0858d5f181(
    action_point: ActionPoint,
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b2e32567a79830faa7134d8cf4de976b9af1a888efa6a348a4d9ecf48ecb64f(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__818b3a1871d46350c2b2a63bcdc255c69e2606bed8874538bb8cfab2a0173f15(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__914b3517803f6f7b3336aa6d44584b6f3f28a8d8c0e04dbeb8990058848b95f6(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc5457eac1e0104d7f7047d43e7ba17ec5e5a103030db601df39c69e2b62ba53(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e3bd848dfa5b364d1bc2f750948cda50530fcf26a50f766c60d84402f629c25(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f72cdb2b7131fc110d260246dfec9e77bbeae7dad233883ae5b3d2a1fa6462e(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18f7d2fbd9c03ffb6988f68a102b38bfba666bfe721b6e8e93823b74ed11e104(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__618d32b2e68b8df805ddc1efe2f210e295699742a5b59ceb6b3eb17004b35258(
    value: ExtensibleBase,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d369243a53460e13a15e17a8fa5ce3aec7f0f665ae9ad2df0b00ad9554845ae(
    bus: _aws_cdk_aws_events_ceddda9d.IEventBus,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad2873bffa0cfdcbec551cfa979c42d4399b322524961fd6adbbcdad95e88e99(
    scope: _constructs_77d1e7e8.Construct,
    resource_arn: builtins.str,
    resource_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa78143937e44300df6567c870280a7ff967c612f7663f779aff230f7d5eea47(
    extension: IExtension,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfa7b2da79d87701fb66c30f8676abf8b75e693f9c3cecc2b951756236f2e517(
    action_point: ActionPoint,
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__893ae21c04ab082282a4a91d53434c6bf8b7264302a91d415fd1b1511b230fad(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1e67d9239f5baa292365454300f5022cc65d189100adf6f1af4544c8a2d11be(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a33a738bc7bd64a70d02a2710dda32915943093f313e8e708ef1598e278cc31f(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3e68727572c2db9c0dcf3b7b2560bb56f6e58dfd923a08379d433cd6e28e221(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3bdb1fa02c9c6cc09af5adca3733bc2bf1215d1376aa76e3b8734ec5182d496(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9f798b0617c9d3a5a67da83bcf2a07731d117f481501f227e0a100301e7057c(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63a5d564ebf401c01446b70c7608c3f0560e657e576b517d158e40120d9ac6c8(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af8832a0d44a8fe047ed6daa99962db2e0474daef522cbc4a3baf77513e50317(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    actions: typing.Sequence[Action],
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3730d907b76b4871efdbd9c4553324fafbf6ba412680637770e2c2fba0bbb1c4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    extension_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56920fdb958facebad8e5dcf817dc5c57807d47e573abf341e76418050084b35(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    extension_id: builtins.str,
    extension_version_number: jsii.Number,
    actions: typing.Optional[typing.Sequence[Action]] = None,
    description: typing.Optional[builtins.str] = None,
    extension_arn: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24ca4d4e414180a1e49401777ce28035f514bfbe81a2dc6f70f18a443bdac1ee(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    content: ConfigurationContent,
    latest_version_number: typing.Optional[jsii.Number] = None,
    version_label: typing.Optional[builtins.str] = None,
    application: IApplication,
    deployment_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    deployment_strategy: typing.Optional[IDeploymentStrategy] = None,
    deploy_to: typing.Optional[typing.Sequence[IEnvironment]] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ConfigurationType] = None,
    validators: typing.Optional[typing.Sequence[IValidator]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ae1a8d2f17b9ca2663d3d3a80ba0c2630d02d53b2ac862048246d5cc50a75ba(
    extension: IExtension,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f0c2aadcb117be66617d3e087ab61602e2764c80b5eefe4b735c8ebb11aee28(
    environment: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eab02d789b656edc985af61760d9027768fe893be7a8b392f6100348f5c72b39(
    environment: IEnvironment,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__072676758a7adfd2c8fc5085433864d9cce6ad895d2edf07c92e2449ac898b17(
    action_point: ActionPoint,
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e6906904ac3ff456f9c5771351a5dbf365223e8a8af0f3c9d7e50e3dc26f9c9(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f889c9f3bc84bcff8f6be8d33cb8864f9c53be1ab9c8966d807a1ce682b649be(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e5bad587ed411e08e86cb527106b96fd4a99b77ddc653700d7bc4cf9b7ee095(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf74da1554db8ffc9a5b9c143e702c2adbe1193e60fe1d93500399a7c125269e(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ff0d6b9be70c35693fe4f8116a81d84623bc1b55926aa61bef8e3973115607c(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f8769538eeb7d06b1c4131e60043297db26c49dca96851fc658e4a4dca603b4(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f08fe3ccf41dd427dada5be4f7948fb2bf4b0a83042d10c61987d0998aebdf3(
    event_destination: IEventDestination,
    *,
    description: typing.Optional[builtins.str] = None,
    latest_version_number: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Sequence[Parameter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89e23b713915e71fb90964317aefa6c4250f1bb304a477477ad7bd67d5eb1af2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bded0b6f2c505902525c2914f2a93aa13cb95bc7606abd473ff9f222c7540bcf(
    value: ExtensibleBase,
) -> None:
    """Type checking stubs"""
    pass
