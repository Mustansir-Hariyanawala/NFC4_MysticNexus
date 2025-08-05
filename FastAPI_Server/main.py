from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.mongodb import connect_to_mongo, close_mongo_connection
from routes.auth_apis import router as auth_router
from routes.user_apis import router as user_router
from routes.chat_apis import router as chat_router
import uvicorn
import os

app = FastAPI(
    title="TSEC NeedForCode API",
    description="FastAPI server with user management and authentication",
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
    return {"message": "Server is Up and Running! GG!"}

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
