#!/bin/bash

# Script to diagnose issues with the ATS Resume Application on Azure
echo "====== Starting Azure App Diagnostics ======"

# Variables - these should match your original deployment
RESOURCE_GROUP="ats-resume-rg"
APP_NAME="ats-resume-app"
ACR_NAME="atsresumeregistry"

# Step 1: Check if the web app exists and its state
echo "Checking if Web App exists and its current state..."
APP_STATE=$(az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query state -o tsv 2>/dev/null)
if [ $? -ne 0 ]; then
  echo "❌ Error: Web App '$APP_NAME' not found in resource group '$RESOURCE_GROUP'"
  exit 1
fi

echo "✅ Web App State: $APP_STATE"

# Step 2: Check container status
echo "Checking container status..."
CONTAINER_STATUS=$(az webapp config container show --resource-group $RESOURCE_GROUP --name $APP_NAME -o json)
echo "$CONTAINER_STATUS"

# Step 3: Check app settings
echo "Checking environment variables (app settings)..."
APP_SETTINGS=$(az webapp config appsettings list --resource-group $RESOURCE_GROUP --name $APP_NAME -o json)
echo "Number of app settings configured: $(echo $APP_SETTINGS | jq length)"
# Not showing actual values for security

# Step 4: Check diagnostic logs
echo "Recent application logs:"
az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME

# Step 5: Check network configuration
echo "Checking network configuration..."
az webapp config show --resource-group $RESOURCE_GROUP --name $APP_NAME --query "{alwaysOn:alwaysOn,cors:cors,http20Enabled:http20Enabled}"

# Step 6: Check custom domains
echo "Checking custom domains..."
az webapp config hostname list --resource-group $RESOURCE_GROUP --webapp-name $APP_NAME

# Step 7: Provide helpful suggestions
echo "====== Troubleshooting Suggestions ======"
echo "1. If the web app state is not 'Running', try restarting: az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo "2. Check that all required environment variables are set correctly"
echo "3. Ensure the container image exists in ACR: az acr repository show-tags --name $ACR_NAME --repository ats-resume"
echo "4. Check application response:"
echo "   - Main app: curl -I https://${APP_NAME}.azurewebsites.net"
echo "   - Health endpoint: curl -I https://${APP_NAME}.azurewebsites.net/health"
echo "   - Health status: curl https://${APP_NAME}.azurewebsites.net/health"
echo "5. For more detailed container logs, enable Docker container logging in the Azure portal"

echo "====== Diagnostics Complete ======"
