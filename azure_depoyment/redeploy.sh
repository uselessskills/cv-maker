#!/bin/bash

# Redeploy script for updating the CV Maker Application on Azure
echo "====== Starting Redeployment Process ======"

# Variables - these should match your original deployment
RESOURCE_GROUP="cv-maker-rg"
APP_NAME="cv-maker-app"
ACR_NAME="cvmakeregistry"

# Source environment variables from dev.env
source dev.env

# Step 1: Rebuild the Docker image
echo "Rebuilding Docker image with Docker Compose..."
docker compose -f docker-compose.azure.yml build --no-cache

# Step 2: Log in to ACR
echo "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

# Step 3: Tag and push the updated image to ACR
echo "Tagging and pushing updated image to ACR..."
docker tag cv-maker-cv-maker-image:latest ${ACR_NAME}.azurecr.io/cv-maker-image:latest
docker push ${ACR_NAME}.azurecr.io/cv-maker-image:latest

# Step 4: Restart the Web App to pick up the new image
echo "Restarting the Web App to apply changes..."
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

# Step 5: Update app settings if they've changed
echo "Updating Web App settings..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
  CHAINLIT_AUTH_SECRET="$CHAINLIT_AUTH_SECRET" \
  AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
  AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
  AZURE_OPENAI_API_VERSION="$AZURE_OPENAI_API_VERSION" \
  AZURE_OPENAI_MODEL="$AZURE_OPENAI_MODEL" \
  USERS="$USERS" \
  WEBSITES_PORT=8000

echo "====== Redeployment Complete ======"
echo "Your updated application should be available at: https://${APP_NAME}.azurewebsites.net"
echo "It may take a few minutes for the changes to propagate."

# Add some diagnostic commands to check status
echo "====== Checking Application Status ======"
echo "Web App State:"
az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query state -o tsv

echo "Container Logs:"
az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME
