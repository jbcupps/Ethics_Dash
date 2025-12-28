import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bson import ObjectId
from pydantic import BaseModel

from app import config
from .blockchain_interface import get_blockchain_interface
from .schemas import hash_data

logger = logging.getLogger(__name__)


class PVBAnchorError(RuntimeError):
    """Raised when anchoring to PVB fails."""


def canonicalize_json(data: Any) -> bytes:
    def _default_serializer(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc).isoformat()
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, BaseModel):
            return value.model_dump()
        if isinstance(value, bytes):
            return value.hex()
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

    canonical = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_default_serializer,
    )
    return canonical.encode("utf-8")


def compute_canonical_hash(data: Dict[str, Any]) -> str:
    canonical_blob = canonicalize_json(data)
    return hash_data(canonical_blob)


def anchor_document(
    data: Dict[str, Any],
    *,
    data_type: str,
    object_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if not config.PVB_ANCHOR_ENABLED:
        return None

    missing = []
    if not config.PVB_ANCHOR_DEVICE_ID:
        missing.append("PVB_ANCHOR_DEVICE_ID")
    if not config.PVB_ANCHOR_SIGNATURE:
        missing.append("PVB_ANCHOR_SIGNATURE")
    if not config.PVB_ANCHOR_DATA_URI:
        missing.append("PVB_ANCHOR_DATA_URI")
    if missing:
        raise PVBAnchorError(f"Missing required PVB anchoring config: {', '.join(missing)}")

    data_hash = compute_canonical_hash(data)
    metadata = {
        "type": data_type,
        "object_id": object_id,
        "canonicalization": "json:sorted_keys",
        "hash": "sha256",
    }
    metadata_payload = json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    blockchain = get_blockchain_interface()
    result = blockchain.submit_data(
        device_id=config.PVB_ANCHOR_DEVICE_ID,
        data_hash=data_hash,
        signature=config.PVB_ANCHOR_SIGNATURE,
        data_uri=config.PVB_ANCHOR_DATA_URI,
        metadata=metadata_payload,
    )

    if not result.get("success"):
        raise PVBAnchorError(result.get("error", "Unknown error anchoring to PVB"))

    return {
        "data_hash": data_hash,
        "transaction_hash": result.get("transaction_hash"),
        "block_number": result.get("block_number"),
        "metadata": metadata,
        "anchored_at": datetime.now(timezone.utc),
    }
