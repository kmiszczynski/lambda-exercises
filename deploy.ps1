# PowerShell Deployment script for Exercises Lambda Function

$FUNCTION_NAME = "exercises-api"
$HANDLER = "src.handler.lambda_handler"
$RUNTIME = "python3.12"
$ZIP_FILE = "lambda_deployment.zip"
$PACKAGE_DIR = "package"

Write-Host "Starting Lambda deployment package creation..." -ForegroundColor Green
Write-Host ""

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $PACKAGE_DIR) {
    Remove-Item $PACKAGE_DIR -Recurse -Force
}
if (Test-Path $ZIP_FILE) {
    Remove-Item $ZIP_FILE -Force
}

# Create package directory
Write-Host "Creating package directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $PACKAGE_DIR | Out-Null

# Install dependencies into package directory
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -t $PACKAGE_DIR --upgrade --quiet

# Copy source code
Write-Host "Copying source code..." -ForegroundColor Yellow
Copy-Item -Path "src\*" -Destination "$PACKAGE_DIR\src" -Recurse -Force

# Create deployment zip
Write-Host "Creating deployment zip..." -ForegroundColor Yellow
Compress-Archive -Path "$PACKAGE_DIR\*" -DestinationPath $ZIP_FILE -Force

# Get zip file size
$zipSize = (Get-Item $ZIP_FILE).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)
Write-Host ""
Write-Host "Deployment package created: $ZIP_FILE ($zipSize bytes / $zipSizeMB MB)" -ForegroundColor Green
Write-Host ""

# Display deployment instructions
Write-Host "To deploy to AWS Lambda, run:" -ForegroundColor Yellow
Write-Host "aws lambda update-function-code --function-name $FUNCTION_NAME --zip-file fileb://$ZIP_FILE" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or upload the $ZIP_FILE file through the AWS Console" -ForegroundColor Yellow
Write-Host ""

# Optional: Pause to keep window open
Read-Host "Press Enter to exit"