import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

# Reading the DB Config Info from the Process Environment
config = {
    "user": urllib.parse.quote_plus(os.getenv("DB_USERNAME", "")),
    "password": urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "")),
    "cluster_name": os.getenv("DB_CLUSTER_NAME", "").lower(),
    "cluster_id": os.getenv("DB_CLUSTER_ID", ""),
    "app_name": os.getenv("DB_CLUSTER_NAME", ""),
    "db_name": os.getenv("DB_NAME", ""),
}

url = f"mongodb+srv://{config['user']}:{config['password']}@{config['cluster_name']}.{config['cluster_id']}.mongodb.net/{config['db_name']}?retryWrites=true&w=majority&appName={config['app_name']}"

async def connect_to_mongo():
    """Create database connection"""
    try:
        MongoDB.client = AsyncIOMotorClient(url)
        MongoDB.database = MongoDB.client[config["db_name"]]
        
        # Test the connection
        await MongoDB.client.admin.command('ping')
        print(f"Connected successfully to MongoDB server. Using database: {config['db_name']}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if MongoDB.client:
        MongoDB.client.close()
        print("Closed MongoDB connection")

def get_database():
    """Get database instance"""
    return MongoDB.database
