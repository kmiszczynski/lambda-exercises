"""DynamoDB service for retrieving exercise data."""

import logging
from typing import List

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ..config import get_aws_config
from ..exceptions import DynamoDbServiceException
from ..models import ExerciseEntity

logger = logging.getLogger(__name__)


class DynamoDbService:
    """Service for DynamoDB operations."""

    def __init__(self):
        """Initialize DynamoDbService with boto3 resource.

        Note: Resource initialization happens during cold start for optimization.
        """
        config = get_aws_config()
        self.dynamodb = boto3.resource("dynamodb", region_name=config.aws_region)
        self.table = self.dynamodb.Table(config.table_name)
        logger.info(f"DynamoDbService initialized - Table: {config.table_name}")

    def get_all_exercises(self) -> List[ExerciseEntity]:
        """Retrieve all exercises from DynamoDB.

        Returns:
            List of ExerciseEntity objects

        Raises:
            DynamoDbServiceException: If scan operation fails
        """
        logger.info("Scanning DynamoDB table for all exercises")

        try:
            exercises = []

            # Use scan with pagination
            scan_kwargs = {}

            while True:
                response = self.table.scan(**scan_kwargs)

                # Convert items to ExerciseEntity objects
                items = response.get("Items", [])
                for item in items:
                    try:
                        entity = ExerciseEntity.from_dynamodb_item(item)
                        exercises.append(entity)
                    except Exception as e:
                        logger.error(
                            f"Failed to parse exercise item: {item.get('exerciseId', 'unknown')}",
                            exc_info=True,
                        )

                # Check if there are more items to scan
                last_evaluated_key = response.get("LastEvaluatedKey")
                if not last_evaluated_key:
                    break

                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

            logger.info(f"Successfully retrieved {len(exercises)} exercises from DynamoDB")
            return exercises

        except (BotoCoreError, ClientError) as e:
            logger.error("DynamoDB error while scanning exercises", exc_info=True)
            raise DynamoDbServiceException(f"Failed to retrieve exercises from DynamoDB: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error while scanning exercises", exc_info=True)
            raise DynamoDbServiceException(f"Unexpected error retrieving exercises: {str(e)}")
