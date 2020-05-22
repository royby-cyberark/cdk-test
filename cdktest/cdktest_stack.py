from aws_cdk import core
from aws_cdk import aws_iam as iam
from cdktest.s3_resource_construct import S3ObjectResource

class CdktestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        tenant_id = core.CfnParameter(self, "TenantId", type="String")

        s3_object = S3ObjectResource(
            scope=self,
            id_='TenantMetadataS3ObjectResource',
            bucket_name="roybtenantisolationtests-tenantmetadatabucket33c3-nvaxiizvlk2n",
            object_key=f"tenant-somethingsomething-dark-side/meta_data_config",
            object_content='{"CelistName": "Yo-Yoma"}',
        )
