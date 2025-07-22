#!/bin/bash

# Run from the root of the CV Maker project

# Azure deployment script for the CV Maker Application
echo "====== Starting Azure Deployment Process ======"

# Variables - change these according to your preferences
RESOURCE_GROUP="cv-maker-rg"
LOCATION="westeurope"  # Choose an Azure region close to your users
APP_NAME="cv-maker-app"
ACR_NAME="cvmakeregistry"  # Azure Container Registry name must be globally unique

# Source environment variables from dev.env
source dev.env

# Ensure the user is added to the docker group for running docker commands without sudo
sudo usermod -aG docker $USER
newgrp docker  # Refresh group membership

# Step 1: Build the Docker image using Docker Compose
echo "Building Docker image with Docker Compose..."
docker compose -f docker-compose.azure.yml build

# Step 2: Create Azure resource group if it doesn't exist
# az account show
echo "Creating resource group if needed..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Step 3: Create Azure Container Registry if it doesn't exist
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Step 4: Log in to ACR
echo "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

# Step 5: Tag and push image to ACR
echo "Tagging and pushing image to ACR..."
docker tag cv-maker-cv-maker-image:latest ${ACR_NAME}.azurecr.io/cv-maker-image:latest
docker push ${ACR_NAME}.azurecr.io/cv-maker-image:latest

# Step 6: Enable admin access for the ACR (needed for Web App)
echo "Enabling admin access for ACR..."
az acr update --name $ACR_NAME --admin-enabled true

# Step 7: Get ACR credentials
echo "Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

# Step 8: Create App Service Plan and Web App for Containers
echo "Creating App Service Plan and Web App for Containers..."
az appservice plan create \
  --resource-group $RESOURCE_GROUP \
  --name ${APP_NAME}-plan \
  --is-linux \
  --sku B1  # Basic tier, adjust as needed

az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan ${APP_NAME}-plan \
  --name $APP_NAME \
  --deployment-container-image-name ${ACR_NAME}.azurecr.io/cv-maker:latest \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

# Step 9: Configure Web App settings (environment variables)
echo "Configuring Web App settings..."
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

# Step 9b: Configure health check
# echo "Configuring health check settings..."
# az webapp config set \
#   --resource-group $RESOURCE_GROUP \
#   --name $APP_NAME \
#   --generic-configurations '{"healthCheckPath": "/health"}'

# Step 10: Configure persistent storage for output files
echo "Creating storage account..."
# Convert APP_NAME to valid storage account name format (lowercase, no hyphens, max 24 chars)
STORAGE_ACCOUNT_NAME=$(echo "${APP_NAME}" | tr -d '-' | tr '[:upper:]' '[:lower:]')
STORAGE_ACCOUNT_NAME="${STORAGE_ACCOUNT_NAME}store"
# Ensure it's no longer than 24 characters
STORAGE_ACCOUNT_NAME=${STORAGE_ACCOUNT_NAME:0:24}
echo "Using storage account name: $STORAGE_ACCOUNT_NAME"

az storage account create \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --allow-blob-public-access false

echo "Creating file share..."
az storage share create \
  --name cvmakershare\
  --account-name $STORAGE_ACCOUNT_NAME

echo "Configuring persistent storage for the web app..."
STORAGE_ACCESS_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT_NAME --query "[0].value" --output tsv)

az webapp config storage-account add \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --custom-id output \
  --storage-type AzureFiles \
  --share-name cvmakershare \
  --account-name $STORAGE_ACCOUNT_NAME \
  --access-key "$STORAGE_ACCESS_KEY" \
  --mount-path /app/output

echo "====== Deployment Complete ======"
echo "Your application should be available at: https://${APP_NAME}.azurewebsites.net"
echo "It may take a few minutes for the application to start and be accessible."
