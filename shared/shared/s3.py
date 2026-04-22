from typing import Any
import logging

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def build_s3_client(
    *,
    region_name: str,
    endpoint_url: str | None = None,
    access_key: str | None = None,
    secret_key: str | None = None,
    signature_version: str = "s3v4",
) -> Any:
    """Create a boto3 S3 client.

    Works for both AWS S3 and S3-compatible services (MinIO, LocalStack).
    Pass `endpoint_url` to target a non-AWS endpoint. Pass `access_key` and
    `secret_key` for explicit credentials; otherwise boto3's default credential
    chain is used (env vars, IAM role, etc.).
    """
    kwargs: dict[str, Any] = {
        "region_name": region_name,
        "config": Config(signature_version=signature_version),
    }

    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url

    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key

    return boto3.client("s3", **kwargs)


def ensure_bucket_exists(client: Any, bucket: str) -> None:
    """Create the bucket if it doesn't exist.

    Useful for local development with MinIO/LocalStack where buckets
    aren't pre-provisioned. In production (AWS S3) buckets should be
    created via Terraform/CloudFormation, but calling this is harmless.
    """
    try:
        client.head_bucket(Bucket=bucket)
        logger.info("S3 bucket '%s' already exists", bucket)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("404", "NoSuchBucket"):
            logger.info("Creating S3 bucket '%s'", bucket)
            client.create_bucket(Bucket=bucket)
        else:
            raise