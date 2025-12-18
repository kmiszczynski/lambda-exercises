"""Response model for exercise data."""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ExerciseResponse:
    """Represents an exercise in the API response."""

    exercise_id: str
    name: str
    description: str
    difficulty_level: str
    image_url: str
    image_url_expiration: str
    instructions: Optional[str] = None
    thumbnail_image_url: Optional[str] = None
    thumbnail_image_url_expiration: Optional[str] = None
    instruction_video_url: Optional[str] = None
    instruction_video_url_expiration: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with camelCase keys, excluding None values
        """
        result = {
            "exerciseId": self.exercise_id,
            "name": self.name,
            "description": self.description,
            "difficultyLevel": self.difficulty_level,
            "imageUrl": self.image_url,
            "imageUrlExpiration": self.image_url_expiration,
        }

        # Only include optional fields if they exist
        if self.instructions:
            result["instructions"] = self.instructions
        if self.thumbnail_image_url:
            result["thumbnailImageUrl"] = self.thumbnail_image_url
        if self.thumbnail_image_url_expiration:
            result["thumbnailImageUrlExpiration"] = self.thumbnail_image_url_expiration
        if self.instruction_video_url:
            result["instructionVideoUrl"] = self.instruction_video_url
        if self.instruction_video_url_expiration:
            result["instructionVideoUrlExpiration"] = self.instruction_video_url_expiration

        return result
