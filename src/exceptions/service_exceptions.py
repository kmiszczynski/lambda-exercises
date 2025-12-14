"""Service exception classes."""


class ServiceException(Exception):
    """Base exception for service errors."""

    def __init__(self, message: str, error_code: str = "SERVICE_ERROR", status_code: int = 500):
        """Initialize ServiceException.

        Args:
            message: Error message
            error_code: Error code for API response
            status_code: HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


class DynamoDbServiceException(ServiceException):
    """Exception for DynamoDB service errors."""

    def __init__(self, message: str):
        """Initialize DynamoDbServiceException.

        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            error_code="DYNAMODB_ERROR",
            status_code=500,
        )


class S3ServiceException(ServiceException):
    """Exception for S3 service errors."""

    def __init__(self, message: str):
        """Initialize S3ServiceException.

        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            error_code="S3_ERROR",
            status_code=500,
        )
