@echo off
REM Deployment script for exercises Lambda function (Windows)
REM This script creates a deployment package with all dependencies

echo Starting Lambda deployment package creation...

REM Clean previous builds
echo Cleaning previous builds...
if exist package rmdir /s /q package
if exist lambda_deployment.zip del lambda_deployment.zip

REM Create package directory
echo Creating package directory...
mkdir package

REM Copy source code (no dependencies needed - Lambda runtime includes boto3)
echo Copying source code...
xcopy /E /I /Y src package\src

REM Create deployment zip
echo Creating deployment zip...
powershell -Command "Compress-Archive -Path package\* -DestinationPath lambda_deployment.zip -Force"

REM Get zip file size
for %%A in (lambda_deployment.zip) do echo Deployment package created: lambda_deployment.zip (%%~zA bytes)

echo Done! Upload lambda_deployment.zip to AWS Lambda.
echo.
echo AWS CLI upload command:
echo aws lambda update-function-code --function-name exercises-api --zip-file fileb://lambda_deployment.zip

pause
