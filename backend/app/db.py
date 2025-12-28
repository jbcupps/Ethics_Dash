from typing import List, Dict, Any, TypeVar, Optional, TypedDict
import logging
from flask import current_app
from bson import ObjectId

from app.pvb.anchoring import anchor_document, PVBAnchorError

logger = logging.getLogger(__name__)
MEMES_COLLECTION_NAME = "ethical_memes"
WELFARE_EVENTS_COLLECTION_NAME = "welfare_events"
AGREEMENTS_COLLECTION_NAME = "agreements"
AGREEMENT_ACTIONS_COLLECTION_NAME = "agreement_actions"

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


def store_welfare_event(event: Dict[str, Any]) -> Optional[str]:
    """Persist a welfare event entry and return the inserted ID."""
    db = get_db()
    try:
        collection = db[WELFARE_EVENTS_COLLECTION_NAME]
        event_doc = dict(event)
        if "_id" not in event_doc:
            event_doc["_id"] = ObjectId()
        anchor_payload = {key: value for key, value in event_doc.items() if key != "pvb_anchor"}
        try:
            anchor_info = anchor_document(
                anchor_payload,
                data_type="assessment",
                object_id=event_doc.get("assessment_id"),
            )
            if anchor_info:
                event_doc["pvb_anchor"] = anchor_info
        except PVBAnchorError:
            logger.exception("Failed to anchor welfare event to PVB")
            raise
        result = collection.insert_one(event_doc)
        logger.info(
            "Stored welfare event",
            extra={"collection": WELFARE_EVENTS_COLLECTION_NAME, "id": str(result.inserted_id)},
        )
        return str(result.inserted_id)
    except Exception:
        logger.error(
            "Error storing welfare event",
            exc_info=True,
            extra={"collection": WELFARE_EVENTS_COLLECTION_NAME},
        )
        raise
