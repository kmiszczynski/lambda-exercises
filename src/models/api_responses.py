"""API response models."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from .exercise_response import ExerciseResponse
from .exercise_list_item_response import ExerciseListItemResponse


@dataclass
class ExerciseDataWrapper:
    """Wrapper for exercise list data in the response."""

    exercises: List[ExerciseListItemResponse]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with exercises list and count
        """
        return {
            "exercises": [exercise.to_dict() for exercise in self.exercises],
            "count": len(self.exercises),
        }


@dataclass
class SingleExerciseDataWrapper:
    """Wrapper for single exercise data in the response."""

    exercise: ExerciseResponse

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with single exercise data
        """
        return {
            "exercise": self.exercise.to_dict(),
        }


@dataclass
class ApiSuccessResponse:
    """Success response structure."""

    data: ExerciseDataWrapper | SingleExerciseDataWrapper

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Success response dictionary
        """
        return {
            "success": True,
            "data": self.data.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@dataclass
class ErrorDetail:
    """Error detail structure."""

    code: str
    message: str
    request_id: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Error detail dictionary
        """
        return {
            "code": self.code,
            "message": self.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requestId": self.request_id,
        }


@dataclass
class ApiErrorResponse:
    """Error response structure."""

    error: ErrorDetail

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Error response dictionary
        """
        return {
            "success": False,
            "error": self.error.to_dict(),
        }
