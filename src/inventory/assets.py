import os
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from typing import Any, Iterable

from boto3.session import Session
from types_boto3_s3 import S3Client

REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "eu-central-1"


@dataclass
class Storage(object):
    arn: str
    name: str
    type: str
    encrypted: bool
    encryption_algorithm: str

    @classmethod
    def fieldnames(cls) -> tuple[str, ...]:
        return tuple(f.name for f in fields(cls))

    def dictfields(self) -> dict[str, Any]:
        return asdict(self)


_S3_ENCRYPTION_BY_DEFAULT = datetime(2023, 1, 5)


# we aren't caching the data for this exercise
def load() -> Iterable[Storage]:
    session = Session(region_name=REGION)

    yield from _load_s3(session)
    yield from _load_rds(session)


def _load_s3(session: Session) -> Iterable[Storage]:
    s3 = session.client(service_name="s3")
    buckets = s3.list_buckets()
    for bucket in buckets["Buckets"]:
        bucket_name = bucket.get("Name", "")
        if not bucket_name:
            continue
        creation_date = bucket.get("CreationDate")
        if creation_date and creation_date.timestamp() >= _S3_ENCRYPTION_BY_DEFAULT.timestamp():
            # see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingEncryption.html
            encrypted = True
            encryption_algorithms = "SSE-S3"
        else:
            encrypted, encryption_algorithms = _s3_detect_encryption_in_rules(s3, bucket_name)

        yield Storage(
            arn=f"arn:aws:s3:::{bucket_name}",
            name=bucket_name,
            type="S3",
            encrypted=encrypted,
            encryption_algorithm=encryption_algorithms,
        )


def _s3_detect_encryption_in_rules(s3: S3Client, bucket_name: str) -> tuple[bool, str]:
    bucket_encryption = s3.get_bucket_encryption(Bucket=bucket_name)
    config = bucket_encryption["ServerSideEncryptionConfiguration"]

    # there should be at least 1 rule with the encryption details
    encrypted = False
    encryption_algorithms: set[str] = set()

    for rule in config["Rules"]:
        bucket_key_enabled = rule.get("BucketKeyEnabled", False)
        if bucket_key_enabled:
            encrypted = True
        else:
            # abort if we find a rule without encryption at the bucket level
            encrypted = False
            encryption_algorithms = set()
            break

        ssenc = rule.get("ApplyServerSideEncryptionByDefault", {})
        algorithm = ssenc.get("SSEAlgorithm", "")
        if algorithm:
            encryption_algorithms.add(algorithm)

    return encrypted, "|".join(encryption_algorithms)


def _load_rds(session: Session) -> Iterable[Storage]:
    rds = session.client(service_name="rds")
    dbinst = rds.describe_db_instances()
    for db in dbinst["DBInstances"]:
        dbid = db.get("DBInstanceIdentifier", "Unknown")
        encrypted = db.get("StorageEncrypted", False)
        name = db.get("DBName", dbid)
        arn = db.get("DBInstanceArn", "Unknown")
        yield Storage(arn=arn, name=name, type="RDS", encrypted=encrypted, encryption_algorithm="KMS")
