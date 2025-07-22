#!/bin/bash

# Get environment variables from dev.env
source dev.env

# Stop any existing container with the same name
echo "Stopping any existing containers..."
sudo docker stop cv-maker-app 2>/dev/null || true
sudo docker rm cv-maker-app 2>/dev/null || true

# echo "Stopping any existing containers..."
# sudo docker stop $(sudo docker ps -q --filter ancestor=cv-maker) 2>/dev/null || true

# Run the Docker container with environment variables
sudo docker run -d \
  -p 8000:8000 \
  --name cv-maker-app \
  -e AZURE_OPENAI_API_KEY="${AZURE_OPENAI_API_KEY}" \
  -e AZURE_OPENAI_ENDPOINT="${AZURE_OPENAI_ENDPOINT}" \
  -e AZURE_OPENAI_API_VERSION="${AZURE_OPENAI_API_VERSION}" \
  -e AZURE_OPENAI_MODEL="${AZURE_OPENAI_MODEL}" \
  -e CHAINLIT_AUTH_SECRET="${CHAINLIT_AUTH_SECRET}" \
  -e USERS="${USERS}" \
  -v "$(pwd)/src:/app/src" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/res:/app/res" \
  ats-resume

# sudo docker run -p 8000:8000 \
#   --env-file dev.env \
#   -e USERS="${USERS:-username:password,username2:password2}" \
#   -v $(pwd)/src:/app/src \
#   -v $(pwd)/output:/app/output \
#   -v $(pwd)/res:/app/res \
#   cv-maker

echo "Container started! The application should be available at http://localhost:8000"
