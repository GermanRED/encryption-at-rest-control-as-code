import os

DEFAULT_REGION = "eu-central-1"


def _ismocked() -> bool:
    aws_mocked = os.environ.get("AWS_MOCKED", "true").lower()
    assert aws_mocked in ("true", "false")
    return aws_mocked == "true"


# this method guarantees the right import order
def setup() -> None:
    if "AWS_DEFAULT_REGION" not in os.environ:
        os.environ["AWS_DEFAULT_REGION"] = DEFAULT_REGION

    if _ismocked():
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"
        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "/tmp/test-credentials"

        # we only import moto if we have to mock boto3
        from moto import mock_aws

        mock = mock_aws()
        mock.start()

        from boto3.session import Session

        region = os.environ.get("AWS_DEFAULT_REGION") or DEFAULT_REGION
        session = Session(region_name=region)

        s3 = session.client(service_name="s3")
        s3.create_bucket(
            Bucket="encryption-at-rest-control-as-code-mock-bucket",
            CreateBucketConfiguration={"LocationConstraint": DEFAULT_REGION},
            ACL="private",
        )
        rds = session.client(service_name="rds")
        rds.create_db_instance(
            DBInstanceIdentifier="eatcac-mock-db",
            AllocatedStorage=5,
            DBInstanceClass="db.t3.micro",
            Engine="mysql",
            MasterUsername="admin",
            MasterUserPassword="0" * 40,
            AvailabilityZone=DEFAULT_REGION,
            BackupRetentionPeriod=0,
            AutoMinorVersionUpgrade=False,
            PubliclyAccessible=False,
            StorageType="standard",
            StorageEncrypted=True,
            MultiTenant=False,
        )
