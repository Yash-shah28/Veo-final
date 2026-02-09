"""
Migration script to add content_type field to existing character projects
This fixes projects created before the content_type field was added
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "veo_studio")

async def migrate_character_projects():
    """Add project_type and content_type fields to character projects"""
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    character_projects = db.character_projects
    
    print("🔍 Finding character projects that need migration...")
    
    # Find all character projects without project_type OR content_type
    projects = await character_projects.find({
        "$or": [
            {"project_type": {"$exists": False}},
            {"content_type": {"$exists": False}}
        ]
    }).to_list(length=1000)
    
    if not projects:
        print("✅ No projects need migration!")
        return
    
    print(f"📦 Found {len(projects)} projects to migrate")
    
    updated_count = 0
    for project in projects:
        topic_mode = project.get("topic_mode", "")
        
        # Determine content_type based on topic_mode
        if topic_mode in ["benefits", "side_effects"]:
            content_type = "food"
        elif topic_mode == "teaching":
            content_type = "educational"
        else:
            # Default to food if unclear
            content_type = "food"
        
        # Always set project_type to "character" for character_projects collection
        update_fields = {
            "project_type": "character",
            "content_type": content_type
        }
        
        # Update the project
        result = await character_projects.update_one(
            {"_id": project["_id"]},
            {"$set": update_fields}
        )
        
        if result.modified_count > 0:
            updated_count += 1
            project_name = project.get("project_name", "Unknown")
            print(f"  ✅ Updated: {project_name}")
            print(f"     → project_type='character', content_type='{content_type}'")
    
    print(f"\n✨ Migration complete! Updated {updated_count} projects")
    client.close()

if __name__ == "__main__":
    print("="*60)
    print("🔧 Character Project Migration Script")
    print("="*60)
    asyncio.run(migrate_character_projects())
