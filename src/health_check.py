from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for Azure App Service"""
    return JSONResponse({"status": "healthy"})
