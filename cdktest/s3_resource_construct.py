from typing import Any

from aws_cdk import (
    core, 
    aws_iam as iam,
    aws_s3 as s3
)
from aws_cdk.core import Duration
from aws_cdk.custom_resources import (
    AwsCustomResource, 
    AwsCustomResourcePolicy, 
    AwsSdkCall, 
    PhysicalResourceId
)
from aws_cdk.aws_iam import PolicyStatement

DEFAULT_S3_READ_TIMEOUT_SEC = 100


class S3ObjectResource(core.Construct):
    """TODO: implement

    Arguments:
        AwsCustomResource {[type]} -- [description]
    """
    def __init__(self, scope: core.Construct, id_: str, bucket_name: str, object_key: str, object_content: Any, log_retention=None,
                 timeout=Duration.seconds(amount=DEFAULT_S3_READ_TIMEOUT_SEC)) -> None:
        super().__init__(scope, id_)

        tenant_config_bucket = s3.Bucket.from_bucket_name(scope=scope, id="TenantConfigBucket", bucket_name=bucket_name)

        on_create = self.get_on_create(bucket_name=bucket_name, object_key=object_key, object_content=object_content)
        on_update = on_create  # Updating an S3 object is actually creating a new version
        on_delete = self.get_on_delete(bucket_name, object_key)

        policy = AwsCustomResourcePolicy.from_sdk_calls(resources=[f'{tenant_config_bucket.bucket_arn}/{object_key}'])
       
        lambda_role = self.get_provisioning_lambda_role()
        # lambda_role = None

        AwsCustomResource(scope=scope, id='AwsCustomResourceTenantMetadataS3Object', policy=policy, log_retention=log_retention, on_create=on_create, on_update=on_update,
                         on_delete=on_delete, resource_type='Custom::AWS-S3-Object', role=lambda_role, timeout=timeout)

    def get_provisioning_lambda_role(self):
        return iam.Role(
            scope=self, 
            id='TenantMetadataConfigS3ObjectLambdaRole', 
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'), 
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")],
        )

    def get_on_create(self, bucket_name, object_key, object_content):
        create_params = {
            "Body": object_content,
            "Bucket": bucket_name,
            "Key": object_key,
        }
            
        #api_version=None uses the latest api
        on_create = AwsSdkCall(
            action='putObject',
            service='S3',
            parameters=create_params,
            # to get a unique physicaid: https://docs.aws.amazon.com/AmazonS3/latest/API/RESTCommonResponseHeaders.html
            physical_resource_id=PhysicalResourceId.from_response('ETag'),
        )
        return on_create

    def get_on_delete(self, bucket_name, object_key):
        delete_params = {
            "Bucket": bucket_name,
            "Key": object_key,
        }

        on_delete = AwsSdkCall(
            action='deleteObject',
            service='S3',
            parameters=delete_params,
        )
        return on_delete
