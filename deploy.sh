#!/bin/bash

# Deployment script for exercises Lambda function
# This script creates a deployment package with all dependencies

set -e

echo "Starting Lambda deployment package creation..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf package lambda_deployment.zip

# Create package directory
echo "Creating package directory..."
mkdir -p package

# Install dependencies into package directory
echo "Installing dependencies..."
pip install -r requirements.txt -t package/ --upgrade

# Copy source code
echo "Copying source code..."
cp -r src package/

# Create deployment zip
echo "Creating deployment zip..."
cd package
zip -r ../lambda_deployment.zip . -x "*.pyc" -x "*__pycache__*" -x "*.dist-info*" -x "*.egg-info*"
cd ..

# Get zip file size
SIZE=$(du -h lambda_deployment.zip | cut -f1)
echo "Deployment package created: lambda_deployment.zip ($SIZE)"

echo "Done! Upload lambda_deployment.zip to AWS Lambda."
echo ""
echo "AWS CLI upload command:"
echo "aws lambda update-function-code --function-name exercises-api --zip-file fileb://lambda_deployment.zip"
