"""S3 service for generating presigned URLs."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config import get_aws_config
from ..exceptions import S3ServiceException

logger = logging.getLogger(__name__)


class S3PresignedUrlService:
    """Service for generating S3 presigned URLs."""

    def __init__(self):
        """Initialize S3PresignedUrlService with boto3 client.

        Note: Client initialization happens during cold start for optimization.
        """
        config = get_aws_config()
        self.s3_client = boto3.client("s3", region_name=config.aws_region)
        self.bucket_name = config.bucket_name
        self.url_expiration_seconds = config.url_expiration_minutes * 60
        logger.info(
            f"S3PresignedUrlService initialized - Bucket: {self.bucket_name}, "
            f"Expiration: {config.url_expiration_minutes} minutes"
        )

    def generate_presigned_url(self, image_key: str) -> Tuple[str, str]:
        """Generate a presigned URL for an S3 object.

        Args:
            image_key: S3 object key

        Returns:
            Tuple of (presigned_url, expiration_time_iso)

        Raises:
            S3ServiceException: If URL generation fails
        """
        if not image_key or not image_key.strip():
            logger.warning("Attempted to generate presigned URL with empty image_key")
            raise S3ServiceException("Image key cannot be null or empty")

        logger.debug(f"Generating presigned URL for key: {image_key}")

        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": image_key},
                ExpiresIn=self.url_expiration_seconds,
            )

            # Calculate expiration time
            expiration_time = datetime.now(timezone.utc) + timedelta(
                seconds=self.url_expiration_seconds
            )
            expiration_iso = expiration_time.isoformat()

            logger.debug(f"Successfully generated presigned URL for key: {image_key}")
            return url, expiration_iso

        except (BotoCoreError, ClientError) as e:
            logger.error(f"S3 error while generating presigned URL for key: {image_key}", exc_info=True)
            raise S3ServiceException(f"Failed to generate presigned URL for image: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error while generating presigned URL for key: {image_key}", exc_info=True
            )
            raise S3ServiceException(f"Unexpected error generating presigned URL: {str(e)}")
