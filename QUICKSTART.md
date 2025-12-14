# Quick Start Guide

This guide will get your Python Lambda function deployed in minutes.

## Prerequisites

- Python 3.11+ installed
- AWS CLI configured with credentials
- AWS account with DynamoDB table and S3 bucket ready

## Step 1: Install Dependencies Locally (Optional - for testing)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Build Deployment Package

**Windows:**
```bash
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

This creates `lambda_deployment.zip`.

## Step 3: Deploy to AWS (Choose One)

### Option A: AWS Console

1. Go to AWS Lambda Console → Create function
2. Function name: `exercises-api`
3. Runtime: Python 3.12
4. Upload `lambda_deployment.zip`
5. Handler: `src.handler.lambda_handler`
6. Set environment variables:
   - `DYNAMODB_TABLE_NAME`: Your table name
   - `S3_BUCKET_NAME`: Your bucket name
   - `PRESIGNED_URL_EXPIRATION_MINUTES`: `60`
7. Adjust memory to 256 MB, timeout to 30 seconds

### Option B: AWS CLI

```bash
# First time deployment
aws lambda create-function \
  --function-name exercises-api \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LAMBDA_ROLE \
  --handler src.handler.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{DYNAMODB_TABLE_NAME=YourTableName,S3_BUCKET_NAME=YourBucketName,PRESIGNED_URL_EXPIRATION_MINUTES=60}"

# Update existing function
aws lambda update-function-code \
  --function-name exercises-api \
  --zip-file fileb://lambda_deployment.zip
```

## Step 4: Set Up API Gateway

1. Go to API Gateway Console → Create REST API
2. Create resource: `/exercises`
3. Add GET method
4. Integration: Lambda Function → `exercises-api`
5. Enable Lambda Proxy Integration
6. Deploy API to stage (e.g., `dev`)

## Step 5: Test

```bash
curl https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/dev/exercises
```

## IAM Permissions Required

Your Lambda execution role needs:

**DynamoDB:**
```json
{
  "Effect": "Allow",
  "Action": ["dynamodb:Scan", "dynamodb:GetItem"],
  "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/YOUR_TABLE"
}
```

**S3:**
```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject"],
  "Resource": "arn:aws:s3:::YOUR_BUCKET/exercises/*"
}
```

**CloudWatch Logs** (Managed Policy):
- Attach `AWSLambdaBasicExecutionRole`

## Troubleshooting

**Package size too large?**
- Make sure you're only installing production dependencies
- boto3 is the only required dependency

**Function timing out?**
- Increase timeout to 30 seconds
- Check DynamoDB table exists and is accessible
- Verify IAM permissions

**Module not found error?**
- Ensure you ran the deployment script correctly
- Verify handler is set to `src.handler.lambda_handler`

**Environment variables not set?**
- Check Lambda configuration → Environment variables
- All required variables must be set

## Next Steps

- Review full [README.md](README.md) for detailed documentation
- Run tests locally: `pytest`
- Monitor with CloudWatch Logs
- Optimize memory allocation based on actual usage

## Performance Tips

1. **Memory**: Start with 256 MB, adjust based on CloudWatch metrics
2. **Timeout**: 30 seconds is good for most cases
3. **Cold Start**: First invocation takes 800-1500ms, subsequent ~50-200ms
4. **Provisioned Concurrency**: Enable for consistent low latency (costs extra)

## Support

- Check [README.md](README.md) for comprehensive documentation
- Review CloudWatch Logs for errors
- Test locally with pytest before deploying
