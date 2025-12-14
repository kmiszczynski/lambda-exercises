# Exercises Lambda Function (Python)

AWS Lambda function for retrieving exercise data from DynamoDB with presigned S3 URLs for images.

## Overview

This Lambda function handles `GET /exercises` requests and returns a list of exercises with:
- Exercise details (name, description, difficulty level)
- Presigned S3 URLs for images (secure, temporary access)
- Optional thumbnail images with presigned URLs
- Mobile-friendly JSON response format

## Tech Stack

- **Runtime**: Python 3.12 (recommended) or Python 3.11+
- **AWS SDK**: boto3 (AWS SDK for Python)
- **Dependencies**: Minimal (boto3 only for production)
- **API Integration**: API Gateway (REST API)
- **Testing**: pytest with mocking support

## Cold Start Optimizations

This implementation includes several optimizations to minimize cold start times:

1. **Service Initialization Outside Handler**: AWS clients and services are initialized at module load time, not during each invocation
2. **Minimal Dependencies**: Only boto3 is required for production, reducing package size
3. **Connection Reuse**: boto3 clients automatically reuse connections across invocations
4. **Type Hints**: Using Python's native type hints instead of heavy runtime validation
5. **Efficient Imports**: Strategic import placement to minimize initialization overhead

## Project Structure

```
exercises-lambda-python/
├── src/
│   ├── handler.py              # Lambda entry point (COLD START OPTIMIZED)
│   ├── models/                 # Data models (dataclasses)
│   │   ├── __init__.py
│   │   ├── exercise_entity.py  # DynamoDB entity
│   │   ├── exercise_response.py # API response model
│   │   └── api_responses.py    # Success/error response structures
│   ├── services/               # Business logic and AWS interactions
│   │   ├── __init__.py
│   │   ├── dynamodb_service.py # DynamoDB operations
│   │   ├── s3_service.py       # S3 presigned URLs
│   │   └── exercise_service.py # Exercise business logic
│   ├── exceptions/             # Custom exceptions
│   │   ├── __init__.py
│   │   └── service_exceptions.py
│   └── config/                 # Configuration
│       ├── __init__.py
│       └── aws_config.py       # Environment variables
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_handler.py
├── requirements.txt            # Python dependencies
├── deploy.sh                   # Deployment script (Linux/Mac)
├── deploy.bat                  # Deployment script (Windows)
├── pytest.ini                  # pytest configuration
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Prerequisites

- **Python**: 3.11+ (Python 3.12 recommended for best Lambda performance)
- **pip**: Latest version
- **AWS Account** with:
  - DynamoDB table created
  - S3 bucket with exercise images
  - IAM role with appropriate permissions

## Local Development Setup

### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

**Windows:**
```bash
set DYNAMODB_TABLE_NAME=Exercises
set S3_BUCKET_NAME=my-exercises-images
set PRESIGNED_URL_EXPIRATION_MINUTES=60
set AWS_REGION=us-east-1
```

**Linux/Mac:**
```bash
export DYNAMODB_TABLE_NAME=Exercises
export S3_BUCKET_NAME=my-exercises-images
export PRESIGNED_URL_EXPIRATION_MINUTES=60
export AWS_REGION=us-east-1
```

### 4. Run Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=src --cov-report=html
```

## DynamoDB Schema

**Table Name**: Configured via `DYNAMODB_TABLE_NAME` environment variable

**Schema**:
```json
{
  "exerciseId": "uuid-1234",                     // String (Partition Key)
  "name": "Push-ups",                            // String
  "description": "Standard push-up exercise...",  // String
  "difficultyLevel": "beginner",                 // String (Values: "beginner", "intermediate", "advanced")
  "imageKey": "exercises/pushups.jpg",           // String (S3 object key - full size)
  "thumbnailImageKey": "exercises/thumbs/pushups_thumb.jpg", // String (S3 object key - thumbnail, optional)
  "createdAt": "2025-12-11T10:00:00Z",          // String (ISO-8601)
  "updatedAt": "2025-12-11T10:00:00Z"           // String (ISO-8601)
}
```

## S3 Bucket Structure

**Bucket Name**: Configured via `S3_BUCKET_NAME` environment variable

**Object Keys Structure**:
```
bucket-name/
├── exercises/                    # Full-size images
│   ├── pushups.jpg
│   ├── squats.jpg
│   └── lunges.jpg
└── exercises/thumbs/             # Thumbnail images (optional)
    ├── pushups_thumb.jpg
    ├── squats_thumb.jpg
    └── lunges_thumb.jpg
```

**Notes**:
- Full-size images: `exercises/{exercise-name}.jpg`
- Thumbnail images: `exercises/thumbs/{exercise-name}_thumb.jpg`
- Thumbnails are optional - if not provided, only the full-size image URL will be returned

## Building Deployment Package

### Option 1: Using Deployment Script (Recommended)

**Windows:**
```bash
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

This creates `lambda_deployment.zip` ready for upload.

### Option 2: Manual Build

**Windows:**
```bash
# Clean previous builds
if exist package rmdir /s /q package
if exist lambda_deployment.zip del lambda_deployment.zip

# Install dependencies
pip install -r requirements.txt -t package\ --upgrade

# Copy source code
xcopy /E /I /Y src package\src

# Create zip
powershell -Command "Compress-Archive -Path package\* -DestinationPath lambda_deployment.zip -Force"
```

**Linux/Mac:**
```bash
# Clean previous builds
rm -rf package lambda_deployment.zip

# Install dependencies
pip install -r requirements.txt -t package/ --upgrade

# Copy source code
cp -r src package/

# Create zip
cd package && zip -r ../lambda_deployment.zip . && cd ..
```

## Deployment to AWS Lambda

### Method 1: AWS Console

#### 1. Create Lambda Function

In AWS Console:
- Navigate to **Lambda** → **Create function**
- **Function name**: `exercises-api`
- **Runtime**: Python 3.12 (or Python 3.11)
- **Architecture**: x86_64
- **Execution role**: Create new role or use existing

#### 2. Upload Deployment Package

- In the function page, go to **Code** tab
- Click **Upload from** → **.zip file**
- Select `lambda_deployment.zip`
- Click **Save**

#### 3. Configure Handler

- **Handler**: `src.handler.lambda_handler`
- Click **Save**

#### 4. Configure Environment Variables

In **Configuration** → **Environment variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `DYNAMODB_TABLE_NAME` | DynamoDB table name | `Exercises` |
| `S3_BUCKET_NAME` | S3 bucket for images | `my-exercises-images` |
| `PRESIGNED_URL_EXPIRATION_MINUTES` | URL validity duration | `60` (1 hour) |
| `AWS_REGION` | AWS region | `us-east-1` |

#### 5. Configure Function Settings

In **Configuration** → **General configuration**:
- **Memory**: 256 MB (recommended, can adjust based on needs)
- **Timeout**: 30 seconds
- **Ephemeral storage**: 512 MB (default)

### Method 2: AWS CLI

```bash
# Create function (first time only)
aws lambda create-function \
  --function-name exercises-api \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LAMBDA_ROLE \
  --handler src.handler.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{DYNAMODB_TABLE_NAME=Exercises,S3_BUCKET_NAME=my-exercises-images,PRESIGNED_URL_EXPIRATION_MINUTES=60}"

# Update function code (subsequent deployments)
aws lambda update-function-code \
  --function-name exercises-api \
  --zip-file fileb://lambda_deployment.zip

# Update environment variables
aws lambda update-function-configuration \
  --function-name exercises-api \
  --environment Variables="{DYNAMODB_TABLE_NAME=Exercises,S3_BUCKET_NAME=my-exercises-images,PRESIGNED_URL_EXPIRATION_MINUTES=60}"
```

## IAM Permissions

The Lambda execution role needs these permissions:

### Required Managed Policy
- `AWSLambdaBasicExecutionRole` (for CloudWatch Logs)

### Custom Inline Policies

**DynamoDB Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Scan",
        "dynamodb:GetItem"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/Exercises"
    }
  ]
}
```

**S3 Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::BUCKET_NAME/exercises/*"
    }
  ]
}
```

## API Gateway Setup

### 1. Create REST API
- Navigate to **API Gateway** → **Create API**
- Choose **REST API**
- API name: `exercises-api`

### 2. Create Resource
- Create resource: `/exercises`

### 3. Create GET Method
- Select `/exercises` resource
- Create method: **GET**
- Integration type: **Lambda Function**
- Lambda Function: `exercises-api`
- Use Lambda Proxy integration: **Yes**

### 4. Enable CORS (if needed)
- Select `/exercises` resource
- Actions → **Enable CORS**
- Confirm

### 5. Deploy API
- Actions → **Deploy API**
- Stage name: `dev` or `prod`
- Deploy

### 6. Test Endpoint

```bash
curl https://API_ID.execute-api.REGION.amazonaws.com/STAGE/exercises
```

## API Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "data": {
    "exercises": [
      {
        "exerciseId": "uuid-1234",
        "name": "Push-ups",
        "description": "Standard push-up exercise...",
        "difficultyLevel": "beginner",
        "imageUrl": "https://bucket.s3.amazonaws.com/exercises/pushups.jpg?X-Amz-Algorithm=...",
        "imageUrlExpiration": "2025-12-12T12:00:00Z",
        "thumbnailImageUrl": "https://bucket.s3.amazonaws.com/exercises/thumbs/pushups_thumb.jpg?X-Amz-Algorithm=...",
        "thumbnailImageUrlExpiration": "2025-12-12T12:00:00Z"
      }
    ],
    "count": 1
  },
  "timestamp": "2025-12-12T11:00:00Z"
}
```

**Note**: `thumbnailImageUrl` and `thumbnailImageUrlExpiration` are optional fields. They will only be included if the exercise has a thumbnail image configured in DynamoDB.

### Error Response (4xx/5xx)

```json
{
  "success": false,
  "error": {
    "code": "DYNAMODB_ERROR",
    "message": "Failed to retrieve exercises from DynamoDB",
    "timestamp": "2025-12-12T11:00:00Z",
    "requestId": "abc-123-def-456"
  }
}
```

### Error Codes

- `INVALID_METHOD` (400): Non-GET HTTP method
- `DYNAMODB_ERROR` (500): DynamoDB operation failed
- `S3_ERROR` (500): S3 presigned URL generation failed
- `INTERNAL_ERROR` (500): Unexpected error

## Performance Characteristics

### Cold Start Performance

With cold start optimizations:
- **First invocation (cold)**: ~800-1500ms (depending on package size)
- **Warm invocations**: ~50-200ms

### Package Size
- **Deployment package**: ~10-15 MB (compressed)
- **Uncompressed**: ~30-50 MB

### Memory Recommendations
- **Minimum**: 128 MB (for simple workloads)
- **Recommended**: 256 MB (balanced performance/cost)
- **High traffic**: 512 MB (faster cold starts)

## Monitoring

### CloudWatch Logs

Logs are automatically sent to CloudWatch Logs:
- **Log Group**: `/aws/lambda/exercises-api`
- View logs in AWS Console → CloudWatch → Log Groups

### CloudWatch Metrics

Monitor in AWS Console → CloudWatch → Metrics → Lambda:
- **Invocations**: Request count
- **Duration**: Execution time
- **Errors**: Error count
- **Throttles**: Throttling events
- **ConcurrentExecutions**: Concurrent invocations

### Sample CloudWatch Logs Insights Queries

**Find errors:**
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

**Average execution time:**
```
fields @duration
| stats avg(@duration) as avg_duration, max(@duration) as max_duration, min(@duration) as min_duration
```

**Cold start analysis:**
```
fields @timestamp, @duration, @initDuration
| filter @type = "REPORT"
| stats count(*) as invocations, avg(@duration) as avg_duration, avg(@initDuration) as avg_cold_start
```

## Troubleshooting

### Common Issues

#### 1. ImportError or ModuleNotFoundError
- **Cause**: Dependencies not included in deployment package
- **Solution**: Run deployment script to include all dependencies

#### 2. Missing Environment Variables
- **Error**: `ValueError: Required environment variable 'X' is not set`
- **Solution**: Set environment variables in Lambda configuration

#### 3. DynamoDB Access Denied
- **Cause**: IAM role lacks DynamoDB permissions
- **Solution**: Add DynamoDB policy to Lambda execution role

#### 4. S3 Presigned URL Not Working
- **Cause**: IAM role lacks S3 permissions or object doesn't exist
- **Solution**:
  - Verify IAM role has `s3:GetObject` permission
  - Check S3 bucket and object keys exist
  - Verify URL hasn't expired

#### 5. Large Package Size
- **Solution**: Remove unnecessary dependencies from requirements.txt
- Only include production dependencies in deployment

## Best Practices Implemented

1. **Type Hints**: All functions use type hints for better IDE support and error detection
2. **Dataclasses**: Using dataclasses for clean, efficient data models
3. **Logging**: Structured logging at appropriate levels (INFO, ERROR, DEBUG)
4. **Error Handling**: Comprehensive error handling with custom exceptions
5. **Separation of Concerns**: Clear separation between handler, services, and models
6. **Cold Start Optimization**: Services initialized at module level
7. **Connection Reuse**: boto3 clients reused across invocations
8. **Documentation**: Comprehensive docstrings and comments
9. **Testing**: Unit tests with mocking for AWS services
10. **Configuration**: Environment-based configuration with defaults

## Python Best Practices

This project follows Python best practices:
- PEP 8 style guide
- Type hints throughout (Python 3.11+ compatible)
- Dataclasses for data models
- Context managers where applicable
- List comprehensions for efficiency
- f-strings for string formatting
- Exception handling with specific exceptions
- Logging instead of print statements

## Comparison with Java Version

| Aspect | Java | Python |
|--------|------|--------|
| **Cold Start** | 2-5 seconds | 0.8-1.5 seconds |
| **Package Size** | 15-30 MB | 10-15 MB |
| **Memory Usage** | 512 MB recommended | 256 MB recommended |
| **Code Lines** | ~800 lines | ~600 lines |
| **Dependencies** | AWS SDK v2, Jackson, Log4j | boto3 only |
| **Type Safety** | Compile-time | Runtime + type hints |

## Contributing

1. Create feature branch
2. Make changes
3. Run tests: `pytest`
4. Ensure code follows PEP 8: `flake8 src tests`
5. Type check (optional): `mypy src`
6. Build deployment package
7. Submit pull request

## License

MIT
