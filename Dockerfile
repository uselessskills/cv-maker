FROM python:3.12-alpine

WORKDIR /app

# Install build dependencies for packages with C extensions
RUN apk add --no-cache build-base gcc musl-dev python3-dev

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set working directory to source files
WORKDIR /app/src

# Add environment variables
ENV CHAINLIT_AUTH_SECRET=${CHAINLIT_AUTH_SECRET}
ENV AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
ENV AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
ENV AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}
ENV AZURE_OPENAI_MODEL=${AZURE_OPENAI_MODEL}
ENV AOI_USERS=${USERS}

# Default port for Chainlit
EXPOSE 8000

# Run the application with explicit host binding to make it accessible from outside the container
CMD ["chainlit", "run", "chatbot.py", "--host", "0.0.0.0"]
