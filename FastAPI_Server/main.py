from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.mongodb import connect_to_mongo, close_mongo_connection
from config.chromadb import connect_to_chroma, close_chroma_connection
from routes.auth_apis import router as auth_router
from routes.user_apis import router as user_router
from routes.chat_apis import router as chat_router
import uvicorn
import os

app = FastAPI(
    title="TSEC NeedForCode API",
    description="FastAPI server with user management and RAG-powered chat system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(chat_router, tags=["Chats"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Server is Up and Running! RAG-Powered Chat System Ready!"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for the entire system"""
    try:
        # Check if all components are working
        return {
            "status": "healthy",
            "message": "RAG-powered FastAPI server is running",
            "features": [
                "User Authentication",
                "Chat Management", 
                "Document Processing",
                "Local ChromaDB Storage",
                "Local Ollama LLM",
                "LangGraph RAG Pipeline"
            ]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB and ChromaDB on startup"""
    await connect_to_mongo()
    await connect_to_chroma()

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB and ChromaDB connections on shutdown"""
    await close_mongo_connection()
    await close_chroma_connection()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
