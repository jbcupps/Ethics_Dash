from typing import List, Dict, Any

def get_all_memes_for_selection() -> List[Dict[str, Any]]:
    \"\"\"Fetches only necessary fields for meme selection prompt.\"\"\"
    db = get_db()
    try:
        # Corrected check
        if db is not None:
            memes_collection = db[MEMES_COLLECTION_NAME]
            # Fetch only name and description, exclude _id unless needed later
            # Cast to list to ensure cursor is exhausted
            memes = list(memes_collection.find({}, {\"_id\": 1, \"name\": 1, \"description\": 1}))
            logger.info(f\"Fetched {len(memes)} memes for selection context.\")
            return memes
        else:
            logger.error(\"Database connection is None in get_all_memes_for_selection.\")
            return []
    except Exception as e:
        logger.error(f\"Error fetching memes for selection: {e}\", exc_info=True)
        return [] 