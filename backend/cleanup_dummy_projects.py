"""
Script to clean up dummy test projects and show real database projects
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "veo_studio")

async def list_and_cleanup_projects():
    """List all projects and delete dummy ones"""
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    character_projects = db.character_projects
    
    print("="*60)
    print("📋 LISTING ALL CHARACTER PROJECTS")
    print("="*60)
    
    # Get all projects
    all_projects = await character_projects.find({}).to_list(length=1000)
    
    print(f"\nTotal projects found: {len(all_projects)}\n")
    
    # Real projects from the database (these should be kept)
    real_project_names = [
        "Yagnesh Modh - teaching",
        "Mr.  Sharma - teaching",
        "Dr. Sharma - teaching",
        "Pizza - side_effects",
        "Hirva Bhatt - benefits",
        "Sundari mehta - benefits",
        "Yagnesh Modh - benefits",
        "Protien Bar - benefits",
        "MOLTBOT - benefits"
    ]
    
    projects_to_keep = []
    projects_to_delete = []
    
    for project in all_projects:
        project_name = project.get("project_name", "Unknown")
        project_id = str(project.get("_id"))
        
        # Check if this is a real project or dummy
        if project_name in real_project_names:
            projects_to_keep.append(project)
            print(f"✅ KEEP: {project_name} (ID: {project_id})")
        else:
            projects_to_delete.append(project)
            print(f"❌ DELETE: {project_name} (ID: {project_id})")
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"Projects to KEEP: {len(projects_to_keep)}")
    print(f"Projects to DELETE: {len(projects_to_delete)}")
    
    if projects_to_delete:
        print(f"\n⚠️  About to DELETE {len(projects_to_delete)} dummy projects:")
        for project in projects_to_delete:
            print(f"   - {project.get('project_name', 'Unknown')}")
        
        response = input("\n❓ Proceed with deletion? (yes/no): ")
        
        if response.lower() == 'yes':
            deleted_count = 0
            for project in projects_to_delete:
                result = await character_projects.delete_one({"_id": project["_id"]})
                if result.deleted_count > 0:
                    deleted_count += 1
                    print(f"🗑️  Deleted: {project.get('project_name', 'Unknown')}")
            
            print(f"\n✨ Cleanup complete! Deleted {deleted_count} projects")
        else:
            print("\n❌ Cleanup cancelled")
    else:
        print("\n✅ No dummy projects to delete!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(list_and_cleanup_projects())
