"""Database module for MongoDB connection and initialization."""
import logging
import os
import ssl
import sys
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidURI
from config import Config


logger = logging.getLogger(__name__)

# Check if we're in production mode
IS_PRODUCTION = os.getenv("FLASK_ENV", "development").lower() == "production"
IS_WINDOWS = sys.platform == 'win32'


class Database:
    """MongoDB database connection manager."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connected = False
        self._connect()
    
    def _ensure_atlas_params(self, mongo_url):
        """Ensure MongoDB Atlas connection string has required parameters."""
        if 'mongodb+srv://' not in mongo_url:
            return mongo_url
        
        # Check if connection string already has query parameters
        if '?' in mongo_url:
            # Check if retryWrites is already present
            if 'retryWrites' not in mongo_url:
                mongo_url += '&retryWrites=true&w=majority'
        else:
            # Add query parameters
            mongo_url += '?retryWrites=true&w=majority'
        
        return mongo_url
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            mongo_url = Config.MONGO_URL
            if not mongo_url or mongo_url.strip() == "":
                logger.warning("MONGO_URL is not set. Database operations will fail.")
                return
            
            # Ensure MongoDB Atlas connection string has proper parameters
            if 'mongodb+srv://' in mongo_url:
                mongo_url = self._ensure_atlas_params(mongo_url)
                logger.info("Ensured MongoDB Atlas connection string has required parameters")
            
            # Try to automatically fix MongoDB URI if password contains special characters
            # Parse and encode username/password if needed
            try:
                # Configure SSL/TLS for MongoDB Atlas connections
                # This fixes SSL handshake issues on Windows
                connection_options = {
                    'serverSelectionTimeoutMS': 10000,  # Increased timeout
                    'connectTimeoutMS': 20000,
                    'socketTimeoutMS': 20000,
                }
                
                # For mongodb+srv (Atlas), ensure TLS is properly configured
                if 'mongodb+srv://' in mongo_url:
                    connection_options['tls'] = True
                    connection_options['tlsAllowInvalidCertificates'] = False
                    
                    # Production-ready SSL/TLS configuration for MongoDB Atlas
                    try:
                        import certifi
                        # Use certifi CA certificates (most reliable for production)
                        connection_options['tlsCAFile'] = certifi.where()
                        
                        # Windows-specific workaround: Allow invalid hostnames (certificates still validated)
                        # This fixes TLSV1_ALERT_INTERNAL_ERROR on Windows while maintaining certificate validation
                        if IS_WINDOWS and not IS_PRODUCTION:
                            connection_options['tlsAllowInvalidHostnames'] = True
                            logger.info("Using certifi CA certificates with Windows hostname workaround (dev mode)")
                        else:
                            logger.info("Using certifi CA certificates for MongoDB Atlas connection")
                    except ImportError:
                        logger.error("certifi is required for MongoDB Atlas connections. Install it: pip install certifi")
                        # Try system default as fallback (less reliable)
                        try:
                            ssl_context = ssl.create_default_context()
                            connection_options['ssl_context'] = ssl_context
                            if IS_WINDOWS and not IS_PRODUCTION:
                                connection_options['tlsAllowInvalidHostnames'] = True
                            logger.warning("Using system default SSL context (certifi recommended)")
                        except Exception as ssl_err:
                            logger.error(f"Could not create SSL context: {ssl_err}")
                            raise ConnectionFailure("SSL context creation failed. Install certifi: pip install certifi")
                
                self.client = MongoClient(mongo_url, **connection_options)
            except InvalidURI:
                # Try to fix the URI by encoding username and password
                try:
                    fixed_url = self._fix_mongodb_uri(mongo_url)
                    logger.info("Attempting to fix MongoDB URI by encoding credentials...")
                    # Configure SSL/TLS for MongoDB Atlas connections
                    connection_options = {
                        'serverSelectionTimeoutMS': 10000,
                        'connectTimeoutMS': 20000,
                        'socketTimeoutMS': 20000,
                    }
                    
                    # For mongodb+srv (Atlas), ensure TLS is properly configured
                    if 'mongodb+srv://' in fixed_url:
                        connection_options['tls'] = True
                        connection_options['tlsAllowInvalidCertificates'] = False
                        # Production-ready SSL configuration
                        try:
                            import certifi
                            connection_options['tlsCAFile'] = certifi.where()
                            # Windows workaround for development
                            if IS_WINDOWS and not IS_PRODUCTION:
                                connection_options['tlsAllowInvalidHostnames'] = True
                        except ImportError:
                            logger.error("certifi is required for MongoDB Atlas. Install it: pip install certifi")
                            try:
                                ssl_context = ssl.create_default_context()
                                connection_options['ssl_context'] = ssl_context
                                if IS_WINDOWS and not IS_PRODUCTION:
                                    connection_options['tlsAllowInvalidHostnames'] = True
                            except Exception:
                                raise ConnectionFailure("SSL configuration failed. Install certifi: pip install certifi")
                    
                    self.client = MongoClient(fixed_url, **connection_options)
                    logger.info("Successfully connected with fixed URI")
                except Exception as fix_error:
                    logger.error("Failed to fix MongoDB URI: %s", fix_error)
                    logger.error("")
                    logger.error("Please update your .env file:")
                    logger.error("If your password contains special characters (@, :, /, etc.), URL-encode them.")
                    logger.error("Example: admin@123 should be admin%%40123")
                    logger.error("Special characters: @ -> %%40, : -> %%3A, / -> %%2F, # -> %%23, etc.")
                    logger.error("")
                    # Don't log full connection string in production (security)
                    if IS_PRODUCTION:
                        logger.error("Your MONGO_URL contains invalid characters")
                    else:
                        logger.error("Your current MONGO_URL: %s", mongo_url)
                    raise InvalidURI(
                        f"Invalid MongoDB URI. Please URL-encode special characters in your password.\n"
                        f"Example: If password is 'admin@123', change it to 'admin%40123' in .env"
                    )
            self.db = self.client[Config.MONGODB_DB_NAME]
            # Test connection with retry (only in development)
            try:
                self.client.admin.command('ping')
            except Exception as ping_error:
                if not IS_PRODUCTION:
                    # Development: retry once (sometimes needed on Windows)
                    logger.warning("Initial ping failed, retrying...")
                    import time
                    time.sleep(1)
                    self.client.admin.command('ping')
                else:
                    # Production: fail fast, no retries
                    raise
            self._connected = True
            logger.info("Connected to MongoDB successfully")
            self._init_collections()
        except InvalidURI as e:
            logger.error("Invalid MongoDB URI: %s", e)
            logger.error("Please check your MONGO_URL in .env file. Make sure special characters are URL-encoded.")
            logger.error("Example: mongodb://username:password@host:port/ or mongodb://localhost:27017/")
            raise
        except ConnectionFailure as e:
            error_str = str(e)
            # Check if it's an SSL/TLS error
            if 'SSL' in error_str or 'TLS' in error_str or 'tlsv1' in error_str.lower():
                logger.error("SSL/TLS handshake failed. This is a common issue on Windows.")
                logger.error("Error: %s", e)
                logger.error("")
                logger.error("Troubleshooting steps for MongoDB Atlas on Windows:")
                logger.error("1. Ensure certifi is installed: pip install certifi")
                logger.error("2. Update pymongo: pip install --upgrade pymongo")
                logger.error("3. Check MongoDB Atlas Network Access - ensure your IP is whitelisted")
                logger.error("   (Go to Atlas Dashboard > Network Access > Add IP Address)")
                logger.error("4. Verify your connection string format:")
                logger.error("   mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority")
                logger.error("5. Ensure password is URL-encoded if it contains special characters")
                logger.error("")
                # In production, do not attempt insecure fallbacks
                if IS_PRODUCTION:
                    logger.error("Production mode: Refusing insecure SSL fallbacks for security.")
                    logger.error("Please ensure:")
                    logger.error("1. certifi is installed: pip install certifi")
                    logger.error("2. MongoDB Atlas Network Access is properly configured")
                    logger.error("3. Connection string is correct and credentials are valid")
                    raise ConnectionFailure(
                        "SSL handshake failed in production mode. "
                        "Insecure fallbacks are disabled for security. "
                        "Please fix SSL configuration."
                    )
                
                # Development mode: Try fallback with increased timeouts only
                logger.warning("Development mode: Attempting fallback connection with increased timeouts...")
                try:
                    fallback_options = {
                        'serverSelectionTimeoutMS': 20000,
                        'connectTimeoutMS': 30000,
                        'socketTimeoutMS': 30000,
                    }
                    # Process connection string for Atlas
                    fallback_url = Config.MONGO_URL
                    if 'mongodb+srv://' in fallback_url:
                        fallback_url = self._ensure_atlas_params(fallback_url)
                        fallback_options['tls'] = True
                        fallback_options['tlsAllowInvalidCertificates'] = False
                        # Use certifi with Windows hostname workaround if needed
                        try:
                            import certifi
                            fallback_options['tlsCAFile'] = certifi.where()
                            # Windows-specific: Allow invalid hostnames (certificates still validated)
                            # This fixes TLSV1_ALERT_INTERNAL_ERROR on Windows
                            if IS_WINDOWS:
                                fallback_options['tlsAllowInvalidHostnames'] = True
                                logger.info("Fallback: Using certifi with Windows hostname workaround")
                            else:
                                logger.info("Fallback: Using certifi CA file for MongoDB Atlas")
                        except ImportError:
                            logger.error("certifi is required. Install it: pip install certifi")
                            raise ConnectionFailure("certifi is required for MongoDB Atlas connections")
                    
                    self.client = MongoClient(fallback_url, **fallback_options)
                    self.db = self.client[Config.MONGODB_DB_NAME]
                    self.client.admin.command('ping')
                    self._connected = True
                    logger.info("Connected successfully with fallback settings")
                    self._init_collections()
                    return
                except Exception as fallback_error:
                    logger.error("Fallback connection also failed: %s", fallback_error)
            
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

