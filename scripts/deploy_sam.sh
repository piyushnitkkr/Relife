#!/bin/bash
# ============================================================
# ReLife AI — Deploy Lambda + DynamoDB + S3 via SAM
# Requires: AWS CLI + SAM CLI installed
# ============================================================

set -e

echo "🌿 ReLife AI — Deploying infrastructure via SAM..."

cd "$(dirname "$0")/../infra"

# Build Lambda packages
sam build --template template.yaml

# Deploy (first time use --guided for interactive setup)
sam deploy \
  --stack-name relife-ai-stack \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Environment=production \
    MongoUri="$MONGO_URI" \
    FrontendUrl="$FRONTEND_URL" \
  --no-confirm-changeset

echo "✅ Infrastructure deployed!"
echo "   Run 'sam list stack-outputs --stack-name relife-ai-stack' to see endpoints"
