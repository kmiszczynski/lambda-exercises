"""Response model for exercise list item data."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExerciseListItemResponse:
    """Represents a minimal exercise item in list API responses."""

    exercise_id: str
    name: str
    difficulty_level: str
    thumbnail_image_url: Optional[str] = None
    thumbnail_image_url_expiration: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with camelCase keys, excluding None values
        """
        result = {
            "exerciseId": self.exercise_id,
            "name": self.name,
            "difficultyLevel": self.difficulty_level,
        }

        # Only include optional fields if they exist
        if self.thumbnail_image_url:
            result["thumbnailImageUrl"] = self.thumbnail_image_url
        if self.thumbnail_image_url_expiration:
            result["thumbnailImageUrlExpiration"] = self.thumbnail_image_url_expiration

        return result