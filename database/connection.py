"""
MongoDB connection management.
Handles connection pooling, health checks, and graceful disconnection.
"""

import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config.settings import Settings


class DatabaseConnection:
    """Singleton MongoDB connection manager."""

    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        """Establish MongoDB connection."""
        if self._client is not None:
            return self._db

        uri = Settings.MONGODB_URI
        if not uri:
            raise ValueError(
                "MONGODB_URI not configured. Please set it in .env file."
            )

        try:
            client_kwargs = {
                "serverSelectionTimeoutMS": 10000,
                "connectTimeoutMS": 10000,
            }
            if "mongodb+srv://" in uri or "tls=true" in uri.lower() or "ssl=true" in uri.lower():
                client_kwargs["tlsCAFile"] = certifi.where()

            self._client = MongoClient(uri, **client_kwargs)
            # Test connection
            self._client.admin.command("ping")
            self._db = self._client[Settings.DATABASE_NAME]
            print(f"[SUCCESS] Connected to MongoDB: {Settings.DATABASE_NAME}")
            return self._db
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"[ERROR] MongoDB connection failed: {e}")
            raise
        except Exception as e:
            print(f"[ERROR] Unexpected connection error: {e}")
            raise

    def get_db(self):
        """Get database instance, connecting if needed."""
        if self._db is None:
            return self.connect()
        return self._db

    def get_collection(self, name):
        """Get a specific collection."""
        db = self.get_db()
        return db[name]

    def health_check(self):
        """Check MongoDB connection health."""
        try:
            if self._client is None:
                return False
            self._client.admin.command("ping")
            return True
        except Exception:
            return False

    def close(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("MongoDB connection closed.")

    def get_stats(self):
        """Get database statistics."""
        try:
            db = self.get_db()
            stats = db.command("dbStats")
            collections = db.list_collection_names()
            collection_counts = {}
            for col in collections:
                collection_counts[col] = db[col].count_documents({})
            return {
                "database": Settings.DATABASE_NAME,
                "collections": len(collections),
                "collection_counts": collection_counts,
                "dataSize": stats.get("dataSize", 0),
                "storageSize": stats.get("storageSize", 0),
            }
        except Exception as e:
            return {"error": str(e)}


# Global connection instance
db_connection = DatabaseConnection()


def get_db():
    """Convenience function to get database."""
    return db_connection.get_db()


# Alias for compatibility
get_database = get_db


def get_collection(name):
    """Convenience function to get collection."""
    return db_connection.get_collection(name)

