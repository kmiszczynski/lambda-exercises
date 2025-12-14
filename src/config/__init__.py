"""Configuration module for AWS clients and environment variables."""

from .aws_config import get_aws_config, AwsConfig

__all__ = ["get_aws_config", "AwsConfig"]
