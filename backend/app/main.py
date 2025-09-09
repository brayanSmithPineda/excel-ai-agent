from fastapi import FastAPI #FastAPI is the web framework we are going to use to create the API
from fastapi.middleware.cors import CORSMiddleware #CORSMiddleware is a middleware that allows us to configure the CORS policy
from app.config.settings import settings
from app.config.database import get_supabase_health

#Create the FastAPI app instance
app = FastAPI(
    title=settings.project_name,
    version="0.1.0", #Version of the API, for now we are going to use a static version
    description="Secure FastAPI backend for Excel AI Agent"
)

#Add CORS middleware for Excel add-in communication (CORS is a way of the server(API) say "Yes it is ok to communicate with me")
#A middleware is a function that runs before the request is processed, like security guard that inspects the request and allows or denies it based on the settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

#Basic healt check endpoint to test the API
@app.get("/health")
async def health_check():
    """Basic API healt check -returns OK if the API is running"""
    return {
        "status": "healthy",
        "message": "Excel AI Agent Backend API is running",
        "version": "0.1.0"
    }

#Supabase health check endpoint
@app.get("/health/supabase")
async def supabase_health_check():
    """Check if the supabase connection is working"""
    health_status = await get_supabase_health()
    return health_status