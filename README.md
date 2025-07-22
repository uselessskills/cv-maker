# CV-Maker [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CV-Maker is a Python-based tool designed to streamline the process of creating professional resumes tailored to the position. It leverages GenAI agentic capabilities using LangGraph to enhance resume generation with intelligent suggestions and adaptive formatting. By utilizing Pydantic models for data validation, adapter patterns for presentation logic, and a modular architecture, the tool ensures a clear separation of concerns and high maintainability. Users can input their resume data in JSON format, which is then processed and rendered into a polished PDF document. The application supports Docker for easy deployment and includes scripts for running locally or deploying to Azure Web App Service.

# Project Architecture

## Key Components of cv-maker-tool (`src/cv_maker_tool.py`)

### Pydantic Models (`src/models/resume_models.py`)

These models define the data structure and validation rules:
- `Header` - Contact information
- `Position` - Job position details
- `Education` - Educational background
- `Experience` - Work experience with multiple positions
- `Project` - Project information
- `SkillElement` - Skills grouped by category
- `ResumeData` - Container for all resume data

### Adapter Pattern (`src/elements/adapters/`)

Adapters wrap Pydantic models and add presentation logic:
- `EducationAdapter` - Formats education entries
- `ExperienceAdapter` - Formats work experience entries
- `ProjectAdapter` - Formats project entries
- `SkillAdapter` - Formats skill entries

### Base Elements (`src/elements/base_element.py`)

- `ModelAdapter` - Generic adapter base class that provides common functionality
- `ResumeElement` - Protocol defining the interface for resume elements

### Sections (`src/sections/resume_section.py`)

- `Section` - Groups related elements under a heading

## How It Works

1. JSON data is loaded and validated using Pydantic models
2. Adapters wrap the models to provide presentation logic
3. Sections organize the elements for rendering
4. The PDF is generated with proper styling and layout

This architecture provides a clear separation of concerns:
- Data validation and structure (Models)
- Presentation logic (Adapters)
- Layout and organization (Sections)

## Agentic Chatbot

The application incorporates a React agent from LangGraph to assist with interactivity and provide intelligent suggestions. This agent uses LangGraph's features to offer context-aware responses, helping users create resumes that are more personalized and polished.

## Monolith python-based webapp

This code utilizes Chainlit, a framework designed for building both backend and frontend components of an application. 
Chainlit simplifies the process of creating interactive user interfaces while integrating seamlessly with backend logic. 
It allows developers to focus on the core functionality of their application by providing tools for rapid development 
and deployment of full-stack solutions.


# Dockerization

## Steps to run
Run `docker compose up --build` to fetch the image, install all dependencies, run the code, and generate the resume inside `src/` directory


### Using the run-with-env.sh Script

We've created a convenient script that handles running the application in Docker with the proper environment variables:

1. Make sure `dev.env` file is properly configured with your Azure OpenAI credentials
2. Make the script executable: `chmod +x run-with-env.sh`
3. Run the script: `./run-with-env.sh`

The application will be available at http://localhost:8000

### Useful Docker Commands

#### Running the Container
```bash
# Run with environment variables from dev.env
./run-with-env.sh

# Or run manually with Docker
sudo docker run -d \
  -p 8000:8000 \
  --name cv-maker-app \
  --env-file dev.env \
  -v "$(pwd)/src:/app/src" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/res:/app/res" \
  cv-maker
```

#### Checking Container Status
```bash
# List all running containers
docker ps

# List all containers (including stopped ones)
docker ps -a
```

#### Container Management
```bash
# Stop the container
docker stop cv-maker-app

# Start an existing container
docker start cv-maker-app

# Remove the container
docker rm cv-maker-app

# View logs with timestamps
docker logs --timestamps cv-maker-app
```

#### Troubleshooting
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Execute a command in the container
sudo docker exec -it cv-maker-app /bin/sh

# Check network connections in the container
sudo docker exec cv-maker-app netstat -tulpn
```

# Azure Deployment

To deploy this application to Azure Web App Service, follow these steps:

1. Make sure you have the Azure CLI installed and are logged in:
   ```bash
   az login
   ```

2. Configure your `dev.env` file (environment variables) with your Azure OpenAI credentials

3. Run the Azure deployment script:
   ```bash
   chmod +x azure-deploy.sh
   ./azure-deploy.sh
   ```

4. The script will:
   - Build your Docker image using Docker Compose
   - Create an Azure Container Registry and push your image
   - Create an Azure Web App for Containers
   - Configure environment variables and persistent storage
   - Deploy your application

5. Once deployment is complete, your application will be available at:
   ```
   https://ats-resume-app.azurewebsites.net
   ```

### Azure Resources Used

- **Azure Container Registry**: Stores your Docker container image
- **Azure Web App for Containers**: Hosts your application
- **Azure Storage Account**: Provides persistent storage for generated resumes

### Monitoring and Management

You can monitor and manage your application through the Azure Portal:
- View logs: Azure Portal > Your Web App > Monitoring > Log stream
- Scale up/down: Azure Portal > Your Web App > Settings > Scale up (App Service plan)
- Configure custom domains: Azure Portal > Your Web App > Settings > Custom domains
