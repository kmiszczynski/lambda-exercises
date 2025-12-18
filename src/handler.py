"""Lambda handler for exercises API.

This module implements the AWS Lambda handler with cold start optimizations:
- Services are initialized outside the handler function
- AWS clients are reused across invocations
- Logging is configured once during module load
"""

import json
import logging
from typing import Any, Dict

from .exceptions import ServiceException
from .models import ApiSuccessResponse, ApiErrorResponse, ErrorDetail, ExerciseDataWrapper, SingleExerciseDataWrapper
from .services import ExerciseService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services outside handler for cold start optimization
# These are created once and reused across Lambda invocations
exercise_service = ExerciseService()

logger.info("Lambda handler initialized - services ready")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle API Gateway requests for exercises.

    This handler processes GET requests and returns exercise data with presigned S3 URLs.
    Supports two routes:
    - GET /exercises - Returns all exercises
    - GET /exercises/{exercise_id} - Returns a single exercise by ID

    Args:
        event: API Gateway proxy request event
        context: Lambda context object

    Returns:
        API Gateway proxy response with status code, headers, and body
    """
    http_method = event.get("httpMethod", "")
    path = event.get("path", "")
    request_id = context.aws_request_id if context else "unknown"

    logger.info(f"Received request - Method: {http_method}, Path: {path}, RequestId: {request_id}")

    try:
        # Validate HTTP method
        if http_method.upper() != "GET":
            logger.warning(f"Invalid HTTP method: {http_method}")
            return _build_error_response(
                status_code=400,
                error_code="INVALID_METHOD",
                message="Only GET method is supported",
                request_id=request_id,
            )

        # Check for path parameters
        path_parameters = event.get("pathParameters", {}) or {}
        exercise_id = path_parameters.get("exercise_id")

        # Route based on presence of exercise_id
        if exercise_id:
            # Get single exercise by ID
            logger.info(f"Fetching single exercise: {exercise_id}")
            exercise = exercise_service.get_exercise_by_id(exercise_id)

            if not exercise:
                logger.warning(f"Exercise not found: {exercise_id}")
                return _build_error_response(
                    status_code=404,
                    error_code="EXERCISE_NOT_FOUND",
                    message=f"Exercise with ID '{exercise_id}' not found",
                    request_id=request_id,
                )

            # Build success response for single exercise
            data_wrapper = SingleExerciseDataWrapper(exercise=exercise)
            success_response = ApiSuccessResponse(data=data_wrapper)

            logger.info(f"Successfully processed request - Returned exercise: {exercise_id}")
            return _build_success_response(status_code=200, data=success_response)
        else:
            # Get all exercises
            exercises = exercise_service.get_all_exercises()

            # Build success response
            data_wrapper = ExerciseDataWrapper(exercises=exercises)
            success_response = ApiSuccessResponse(data=data_wrapper)

            logger.info(f"Successfully processed request - Returned {len(exercises)} exercises")
            return _build_success_response(status_code=200, data=success_response)

    except ServiceException as e:
        logger.error(f"Service error occurred: {e.error_code} - {e.message}", exc_info=True)
        return _build_error_response(
            status_code=e.status_code,
            error_code=e.error_code,
            message=e.message,
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Unexpected error occurred", exc_info=True)
        return _build_error_response(
            status_code=500,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred while processing your request",
            request_id=request_id,
        )


def _build_success_response(status_code: int, data: ApiSuccessResponse) -> Dict[str, Any]:
    """Build a successful API Gateway response.

    Args:
        status_code: HTTP status code
        data: Success response data

    Returns:
        API Gateway response dictionary
    """
    try:
        body = json.dumps(data.to_dict())
    except Exception as e:
        logger.error("Failed to serialize success response", exc_info=True)
        return _build_error_response(
            status_code=500,
            error_code="SERIALIZATION_ERROR",
            message="Failed to serialize response",
            request_id="unknown",
        )

    return {
        "statusCode": status_code,
        "headers": _get_cors_headers(),
        "body": body,
    }


def _build_error_response(
    status_code: int, error_code: str, message: str, request_id: str
) -> Dict[str, Any]:
    """Build an error API Gateway response.

    Args:
        status_code: HTTP status code
        error_code: Error code
        message: Error message
        request_id: Request ID for tracking

    Returns:
        API Gateway response dictionary
    """
    try:
        error_detail = ErrorDetail(code=error_code, message=message, request_id=request_id)
        error_response = ApiErrorResponse(error=error_detail)
        body = json.dumps(error_response.to_dict())
    except Exception as e:
        logger.error("Failed to serialize error response", exc_info=True)
        # Fallback to simple JSON string
        body = json.dumps(
            {
                "success": False,
                "error": {
                    "code": error_code,
                    "message": message,
                    "requestId": request_id,
                },
            }
        )

    return {
        "statusCode": status_code,
        "headers": _get_cors_headers(),
        "body": body,
    }


def _get_cors_headers() -> Dict[str, str]:
    """Get CORS headers for API responses.

    Returns:
        Dictionary of CORS headers
    """
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
