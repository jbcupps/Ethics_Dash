# MongoDB Data Initialization

This directory contains scripts for initializing the MongoDB database with ethical terminology data.

## Files

- `init-mongo.js` - Original import script that contained a partial list of ethical terms
- `improved-meme-import.js` - Enhanced import script with the complete set of ethical terms from Meme_Inventory.md

## Improvements

The improved script (`improved-meme-import.js`) addresses several limitations in the original script:

1. **Complete Data Import**: The original script only imported a subset of terms from the Meme_Inventory.md file. The improved script includes all terms from the complete document.

2. **Better Categorization**: Terms are now properly categorized according to their source section in the Meme_Inventory.md file.

3. **Semantic Keywords**: The script automatically extracts relevant keywords from each definition to improve searchability.

4. **Consistent Structure**: All entries follow a consistent structure with appropriate ethical dimensions mapped from their categories.

## Usage

The Docker Compose configuration has been updated to use the improved script. When you start the Docker container for MongoDB, it will automatically import the complete dataset if the collection is empty.

To manually verify the import after starting the containers:

```powershell
# Check the document count
docker exec ethical-review-mongodb mongosh --quiet --eval "db.getSiblingDB('ethical_memes_db').ethical_memes.countDocuments()"

# View a sample document
docker exec ethical-review-mongodb mongosh --quiet --eval "db.getSiblingDB('ethical_memes_db').ethical_memes.findOne()"
```

## Troubleshooting

If the import doesn't work as expected:

1. Check that the Docker volume for MongoDB data is properly set up
2. Verify that the initialization script is correctly mounted in the Docker container
3. Examine Docker logs for any MongoDB startup errors
4. If needed, manually delete the MongoDB volume to force a fresh import 