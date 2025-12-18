"""Exercise service for business logic."""

import logging
from typing import List

from ..models import ExerciseEntity, ExerciseResponse
from .dynamodb_service import DynamoDbService
from .s3_service import S3PresignedUrlService

logger = logging.getLogger(__name__)


class ExerciseService:
    """Service for exercise-related business logic."""

    def __init__(
        self,
        dynamodb_service: DynamoDbService | None = None,
        s3_service: S3PresignedUrlService | None = None,
    ):
        """Initialize ExerciseService with dependencies.

        Args:
            dynamodb_service: DynamoDB service instance (optional, will create if not provided)
            s3_service: S3 service instance (optional, will create if not provided)
        """
        self.dynamodb_service = dynamodb_service or DynamoDbService()
        self.s3_service = s3_service or S3PresignedUrlService()
        logger.info("ExerciseService initialized")

    def get_all_exercises(self) -> List[ExerciseResponse]:
        """Retrieve all exercises with presigned URLs.

        Returns:
            List of ExerciseResponse objects with presigned S3 URLs

        Raises:
            ServiceException: If retrieval or conversion fails
        """
        logger.info("Fetching all exercises")

        entities = self.dynamodb_service.get_all_exercises()
        responses = []

        for entity in entities:
            try:
                response = self._convert_to_response(entity)
                responses.append(response)
            except Exception as e:
                logger.error(
                    f"Failed to convert exercise entity to response for exerciseId: {entity.exercise_id}",
                    exc_info=True,
                )
                # Continue processing other exercises

        logger.info(f"Successfully converted {len(responses)} exercises to responses")
        return responses

    def get_exercise_by_id(self, exercise_id: str) -> ExerciseResponse | None:
        """Retrieve a single exercise by ID with presigned URLs.

        Args:
            exercise_id: The exercise ID to retrieve

        Returns:
            ExerciseResponse with presigned S3 URLs, or None if not found

        Raises:
            ServiceException: If retrieval or conversion fails
        """
        logger.info(f"Fetching exercise with ID: {exercise_id}")

        entity = self.dynamodb_service.get_exercise_by_id(exercise_id)

        if not entity:
            logger.info(f"Exercise not found: {exercise_id}")
            return None

        try:
            response = self._convert_to_response(entity)
            logger.info(f"Successfully converted exercise to response: {exercise_id}")
            return response
        except Exception as e:
            logger.error(
                f"Failed to convert exercise entity to response for exerciseId: {exercise_id}",
                exc_info=True,
            )
            raise

    def _convert_to_response(self, entity: ExerciseEntity) -> ExerciseResponse:
        """Convert ExerciseEntity to ExerciseResponse with presigned URLs.

        Args:
            entity: ExerciseEntity from DynamoDB

        Returns:
            ExerciseResponse with presigned URLs
        """
        # Generate presigned URL for main image
        image_url, image_expiration = self.s3_service.generate_presigned_url(entity.image_key)

        response = ExerciseResponse(
            exercise_id=entity.exercise_id,
            name=entity.name,
            description=entity.description,
            difficulty_level=entity.difficulty_level,
            image_url=image_url,
            image_url_expiration=image_expiration,
            instructions=entity.instructions,
        )

        # Generate presigned URL for thumbnail if it exists
        if entity.thumbnail_image_key and entity.thumbnail_image_key.strip():
            thumbnail_url, thumbnail_expiration = self.s3_service.generate_presigned_url(
                entity.thumbnail_image_key
            )
            response.thumbnail_image_url = thumbnail_url
            response.thumbnail_image_url_expiration = thumbnail_expiration

        return response
