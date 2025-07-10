from typing import List, Dict, Any, TypeVar, Optional, TypedDict
import logging
from flask import current_app

logger = logging.getLogger(__name__)
MEMES_COLLECTION_NAME = "ethical_memes"

class DatabaseConnectionError(Exception):
    """Raised when the database connection is not initialized."""
    pass


def get_db():
    """Return the MongoDB database handle from the Flask app."""
    db = getattr(current_app, "db", None)
    if db is None:
        logger.error("No database connection available", exc_info=True)
        raise DatabaseConnectionError("Database connection is not initialized")
    return db


T = TypeVar("T", bound=Dict[str, Any])

def fetch_documents(
    collection_name: str,
    query_filter: Optional[Dict[str, Any]] = None,
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[List[tuple]] = None,
    limit: Optional[int] = None,
) -> List[T]:
    """Fetch documents from the specified MongoDB collection."""

    db = get_db()
    try:
        collection = db[collection_name]
        cursor = collection.find(query_filter or {}, projection or {})
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        docs: List[T] = list(cursor)
        logger.info(
            "Fetched documents",
            extra={
                "collection": collection_name,
                "filter": query_filter or {},
                "projection": projection,
                "count": len(docs),
            },
        )
        return docs
    except Exception:
        logger.error(
            "Error fetching documents",
            exc_info=True,
            extra={
                "collection": collection_name,
                "filter": query_filter or {},
                "projection": projection,
            },
        )
        raise


class MemeSelection(TypedDict):
    """Type-safe dict for meme selection fields."""
    _id: Any
    name: str
    description: str


def get_all_memes_for_selection() -> List[MemeSelection]:
    """
    Fetch only the necessary fields for a meme selection prompt.
    """
    projection = {"_id": 1, "name": 1, "description": 1}
    return fetch_documents(MEMES_COLLECTION_NAME, projection=projection) 