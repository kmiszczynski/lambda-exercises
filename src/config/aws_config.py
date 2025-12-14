"""AWS configuration and environment variable handling."""

import os
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AwsConfig:
    """AWS configuration from environment variables."""

    table_name: str
    bucket_name: str
    url_expiration_minutes: int
    aws_region: str

    @classmethod
    def from_env(cls) -> "AwsConfig":
        """Load configuration from environment variables.

        Returns:
            AwsConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        table_name = os.environ.get("DYNAMODB_TABLE_NAME")
        bucket_name = os.environ.get("S3_BUCKET_NAME")

        if not table_name:
            raise ValueError("Required environment variable 'DYNAMODB_TABLE_NAME' is not set")
        if not bucket_name:
            raise ValueError("Required environment variable 'S3_BUCKET_NAME' is not set")

        url_expiration = int(os.environ.get("PRESIGNED_URL_EXPIRATION_MINUTES", "60"))
        aws_region = os.environ.get("AWS_REGION", "us-east-1")

        logger.info(
            f"AWS Config loaded - Region: {aws_region}, Table: {table_name}, "
            f"Bucket: {bucket_name}, URL Expiration: {url_expiration} minutes"
        )

        return cls(
            table_name=table_name,
            bucket_name=bucket_name,
            url_expiration_minutes=url_expiration,
            aws_region=aws_region,
        )


# Singleton instance - loaded once during cold start
_aws_config: AwsConfig | None = None


def get_aws_config() -> AwsConfig:
    """Get the AWS configuration singleton.

    Returns:
        AwsConfig instance
    """
    global _aws_config
    if _aws_config is None:
        _aws_config = AwsConfig.from_env()
    return _aws_config
