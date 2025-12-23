"""Database module for MongoDB connection and initialization."""
import logging
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidURI
from config import Config


logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connected = False
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            mongo_url = Config.MONGO_URL
            if not mongo_url or mongo_url.strip() == "":
                logger.warning("MONGO_URL is not set. Database operations will fail.")
                return
            
            # Try to automatically fix MongoDB URI if password contains special characters
            # Parse and encode username/password if needed
            try:
                self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            except InvalidURI:
                # Try to fix the URI by encoding username and password
                try:
                    fixed_url = self._fix_mongodb_uri(mongo_url)
                    logger.info("Attempting to fix MongoDB URI by encoding credentials...")
                    self.client = MongoClient(fixed_url, serverSelectionTimeoutMS=5000)
                    logger.info("Successfully connected with fixed URI")
                except Exception as fix_error:
                    logger.error("Failed to fix MongoDB URI: %s", fix_error)
                    logger.error("")
                    logger.error("Please update your .env file:")
                    logger.error("If your password contains special characters (@, :, /, etc.), URL-encode them.")
                    logger.error("Example: admin@123 should be admin%%40123")
                    logger.error("Special characters: @ -> %%40, : -> %%3A, / -> %%2F, # -> %%23, etc.")
                    logger.error("")
                    logger.error("Your current MONGO_URL: %s", mongo_url)
                    raise InvalidURI(
                        f"Invalid MongoDB URI. Please URL-encode special characters in your password.\n"
                        f"Example: If password is 'admin@123', change it to 'admin%40123' in .env"
                    )
            self.db = self.client[Config.MONGODB_DB_NAME]
            # Test connection
            self.client.admin.command('ping')
            self._connected = True
            logger.info("Connected to MongoDB successfully")
            self._init_collections()
        except InvalidURI as e:
            logger.error("Invalid MongoDB URI: %s", e)
            logger.error("Please check your MONGO_URL in .env file. Make sure special characters are URL-encoded.")
            logger.error("Example: mongodb://username:password@host:port/ or mongodb://localhost:27017/")
            raise
        except ConnectionFailure as e:
            logger.error("Failed to connect to MongoDB: %s", e)
            logger.error("Please ensure MongoDB is running and MONGO_URL is correct in .env file")
            raise
        except Exception as e:
            logger.error("Unexpected error connecting to MongoDB: %s", e)
            raise
    
    def _fix_mongodb_uri(self, uri):
        """Fix MongoDB URI by URL-encoding username and password."""
        # Parse MongoDB URI manually to handle passwords with special characters
        # Format: mongodb+srv://username:password@host/database
        # We need to find the last @ before the hostname (which starts with a letter or number)
        
        # Find protocol
        if uri.startswith('mongodb+srv://'):
            protocol = 'mongodb+srv://'
            rest = uri[14:]  # Remove 'mongodb+srv://'
        elif uri.startswith('mongodb://'):
            protocol = 'mongodb://'
            rest = uri[10:]  # Remove 'mongodb://'
        else:
            return uri
        
        # Find the last @ that's followed by a hostname (starts with letter/number, not special char)
        # We'll work backwards from the end
        at_positions = [i for i, char in enumerate(rest) if char == '@']
        
        if not at_positions:
            return uri  # No credentials, return as-is
        
        # Find the last @ that's likely the separator (before hostname)
        # Hostname typically starts after @ and contains dots or is a domain
        last_at = at_positions[-1]
        
        # Everything before the last @ is credentials
        creds_part = rest[:last_at]
        host_part = rest[last_at + 1:]
        
        # Split credentials on first colon
        if ':' in creds_part:
            username, password = creds_part.split(':', 1)
            # URL-encode username and password
            encoded_username = quote_plus(username)
            encoded_password = quote_plus(password)
            return f"{protocol}{encoded_username}:{encoded_password}@{host_part}"
        else:
            # Only username, no password
            encoded_username = quote_plus(creds_part)
            return f"{protocol}{encoded_username}@{host_part}"
    
    def _init_collections(self):
        """Initialize MongoDB collections with required indexes."""
        if not self._connected:
            return
            
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
        """Get a collection from the database."""
        if not self._connected:
            raise ConnectionError("Database is not connected. Please check MongoDB connection.")
        return self.db[collection_name]


# Global database instance
db = Database()

