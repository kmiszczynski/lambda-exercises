"""DynamoDB entity model for exercises."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExerciseEntity:
    """Represents an exercise entity from DynamoDB."""

    exercise_id: str
    name: str
    description: str
    difficulty_level: str
    image_key: Optional[str] = None
    instructions: Optional[str] = None
    thumbnail_image_key: Optional[str] = None
    instruction_video_key: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dynamodb_item(cls, item: dict) -> "ExerciseEntity":
        """Create an ExerciseEntity from a DynamoDB item.

        Args:
            item: DynamoDB item dictionary

        Returns:
            ExerciseEntity instance
        """
        return cls(
            exercise_id=item.get("exerciseId", ""),
            name=item.get("name", ""),
            description=item.get("description", ""),
            difficulty_level=item.get("difficultyLevel", ""),
            image_key=item.get("imageKey"),
            instructions=item.get("instructions"),
            thumbnail_image_key=item.get("thumbnailImageKey"),
            instruction_video_key=item.get("instructionVideoKey"),
            created_at=item.get("createdAt"),
            updated_at=item.get("updatedAt"),
        )
