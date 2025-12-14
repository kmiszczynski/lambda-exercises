"""Custom exceptions for the exercises Lambda function."""

from .service_exceptions import ServiceException, DynamoDbServiceException, S3ServiceException

__all__ = ["ServiceException", "DynamoDbServiceException", "S3ServiceException"]
