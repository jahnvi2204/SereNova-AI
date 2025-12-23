"""Database module for MongoDB connection and initialization."""
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config


logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
        self._init_collections()
    
    def _connect(self):
        try:
            self.client = MongoClient(Config.MONGO_URL)
            self.db = self.client[Config.MONGODB_DB_NAME]
            # Test connection
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
        except ConnectionFailure as e:
            logger.error("Failed to connect to MongoDB: %s", e)
            raise
    
    def _init_collections(self):
    
        try:
            # Users collection
            users_collection = self.db.users
            users_collection.create_index("email", unique=True)
            logger.info("Users collection initialized with email index")
            
            # Chat sessions collection
            sessions_collection = self.db.chat_sessions
            sessions_collection.create_index("user_id")
            sessions_collection.create_index([("user_id", 1), ("last_updated", -1)])
            logger.info("Chat sessions collection initialized")
            
            # Messages collection
            messages_collection = self.db.messages
            messages_collection.create_index("session_id")
            messages_collection.create_index([("session_id", 1), ("created_at", 1)])
            logger.info("Messages collection initialized")
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error("Error initializing database: %s", e)
            raise
    
    def get_collection(self, collection_name):
        return self.db[collection_name]


# Global database instance
db = Database()

