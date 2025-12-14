"""Unit tests for the Lambda handler."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

# Set required environment variables for testing
os.environ["DYNAMODB_TABLE_NAME"] = "test-table"
os.environ["S3_BUCKET_NAME"] = "test-bucket"
os.environ["AWS_REGION"] = "us-east-1"


class TestLambdaHandler:
    """Test cases for the Lambda handler."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        # Mock context
        self.context = MagicMock()
        self.context.request_id = "test-request-id"

    @patch("src.handler.exercise_service")
    def test_handler_success(self, mock_service):
        """Test successful GET request."""
        from src.handler import lambda_handler
        from src.models import ExerciseResponse

        # Mock service response
        mock_exercises = [
            ExerciseResponse(
                exercise_id="ex-1",
                name="Push-ups",
                description="Standard push-up",
                difficulty_level="beginner",
                image_url="https://example.com/image.jpg",
                image_url_expiration="2025-12-12T12:00:00Z",
            )
        ]
        mock_service.get_all_exercises.return_value = mock_exercises

        # Create test event
        event = {
            "httpMethod": "GET",
            "path": "/exercises",
        }

        # Execute handler
        response = lambda_handler(event, self.context)

        # Assertions
        assert response["statusCode"] == 200
        assert "application/json" in response["headers"]["Content-Type"]

        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["data"]["count"] == 1
        assert len(body["data"]["exercises"]) == 1
        assert body["data"]["exercises"][0]["exerciseId"] == "ex-1"

    def test_handler_invalid_method(self):
        """Test handler with invalid HTTP method."""
        from src.handler import lambda_handler

        event = {
            "httpMethod": "POST",
            "path": "/exercises",
        }

        response = lambda_handler(event, self.context)

        assert response["statusCode"] == 400

        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "INVALID_METHOD"

    @patch("src.handler.exercise_service")
    def test_handler_service_exception(self, mock_service):
        """Test handler when service raises exception."""
        from src.handler import lambda_handler
        from src.exceptions import DynamoDbServiceException

        # Mock service to raise exception
        mock_service.get_all_exercises.side_effect = DynamoDbServiceException(
            "DynamoDB connection failed"
        )

        event = {
            "httpMethod": "GET",
            "path": "/exercises",
        }

        response = lambda_handler(event, self.context)

        assert response["statusCode"] == 500

        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "DYNAMODB_ERROR"

    @patch("src.handler.exercise_service")
    def test_handler_unexpected_exception(self, mock_service):
        """Test handler when unexpected exception occurs."""
        from src.handler import lambda_handler

        # Mock service to raise unexpected exception
        mock_service.get_all_exercises.side_effect = Exception("Unexpected error")

        event = {
            "httpMethod": "GET",
            "path": "/exercises",
        }

        response = lambda_handler(event, self.context)

        assert response["statusCode"] == 500

        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["code"] == "INTERNAL_ERROR"

    def test_cors_headers_present(self):
        """Test that CORS headers are present in response."""
        from src.handler import lambda_handler

        event = {
            "httpMethod": "POST",  # Will trigger error, but should still have CORS
            "path": "/exercises",
        }

        response = lambda_handler(event, self.context)

        assert "Access-Control-Allow-Origin" in response["headers"]
        assert response["headers"]["Access-Control-Allow-Origin"] == "*"
        assert "Access-Control-Allow-Methods" in response["headers"]


class TestModels:
    """Test cases for data models."""

    def test_exercise_entity_from_dynamodb_item(self):
        """Test ExerciseEntity creation from DynamoDB item."""
        from src.models import ExerciseEntity

        item = {
            "exerciseId": "ex-1",
            "name": "Push-ups",
            "description": "Standard push-up",
            "difficultyLevel": "beginner",
            "imageKey": "exercises/pushups.jpg",
            "thumbnailImageKey": "exercises/thumbs/pushups_thumb.jpg",
            "createdAt": "2025-12-12T10:00:00Z",
            "updatedAt": "2025-12-12T10:00:00Z",
        }

        entity = ExerciseEntity.from_dynamodb_item(item)

        assert entity.exercise_id == "ex-1"
        assert entity.name == "Push-ups"
        assert entity.thumbnail_image_key == "exercises/thumbs/pushups_thumb.jpg"

    def test_exercise_response_to_dict(self):
        """Test ExerciseResponse serialization."""
        from src.models import ExerciseResponse

        response = ExerciseResponse(
            exercise_id="ex-1",
            name="Push-ups",
            description="Standard push-up",
            difficulty_level="beginner",
            image_url="https://example.com/image.jpg",
            image_url_expiration="2025-12-12T12:00:00Z",
        )

        data = response.to_dict()

        assert data["exerciseId"] == "ex-1"
        assert data["name"] == "Push-ups"
        assert "thumbnailImageUrl" not in data  # Should not include None values

    def test_exercise_response_with_thumbnail(self):
        """Test ExerciseResponse with thumbnail."""
        from src.models import ExerciseResponse

        response = ExerciseResponse(
            exercise_id="ex-1",
            name="Push-ups",
            description="Standard push-up",
            difficulty_level="beginner",
            image_url="https://example.com/image.jpg",
            image_url_expiration="2025-12-12T12:00:00Z",
            thumbnail_image_url="https://example.com/thumb.jpg",
            thumbnail_image_url_expiration="2025-12-12T12:00:00Z",
        )

        data = response.to_dict()

        assert "thumbnailImageUrl" in data
        assert data["thumbnailImageUrl"] == "https://example.com/thumb.jpg"
