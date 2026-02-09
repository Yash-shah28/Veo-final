"""
Script to check user ownership and fix project user_id
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "veo_studio")

async def check_and_fix_user_projects():
    """Check which user owns which projects and fix user_id"""
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    character_projects = db.character_projects
    users = db.users
    
    print("="*60)
    print("👥 CHECKING PROJECT OWNERSHIP")
    print("="*60)
    
    # Get all users
    all_users = await users.find({}).to_list(100)
    print(f"\n📋 Found {len(all_users)} users:")
    for user in all_users:
        user_id = str(user.get("_id"))
        email = user.get("email", "Unknown")
        print(f"  - {email} (ID: {user_id})")
    
    # Get all character projects
    all_projects = await character_projects.find({}).to_list(100)
    print(f"\n\n📦 Found {len(all_projects)} character projects:")
    
    # Group projects by user_id
    projects_by_user = {}
    for project in all_projects:
        user_id = project.get("user_id", "NO_USER")
        if user_id not in projects_by_user:
            projects_by_user[user_id] = []
        projects_by_user[user_id].append(project)
    
    # Show projects for each user
    for user_id, projects in projects_by_user.items():
        # Find user email
        user = await users.find_one({"_id": user_id}) if user_id != "NO_USER" else None
        email = user.get("email", "Unknown") if user else "NO_USER"
        
        print(f"\n  User: {email} ({user_id})")
        print(f"  Projects ({len(projects)}):")
        for p in projects:
            print(f"    - {p.get('project_name')} (ID: {p.get('_id')})")
    
    print(f"\n\n{'='*60}")
    print("🔧 FIX OPTIONS")
    print("="*60)
    print("1. Move all projects to a specific user")
    print("2. Delete dummy projects (food1, bvcx, ro4, etc.)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1/2/3): ")
    
    if choice == "1":
        print("\n📧 Available users:")
        for i, user in enumerate(all_users):
            print(f"  {i + 1}. {user.get('email')} (ID: {user.get('_id')})")
        
        user_choice = int(input("\nSelect user number: ")) - 1
        target_user_id = str(all_users[user_choice].get("_id"))
        target_email = all_users[user_choice].get("email")
        
        print(f"\n⚠️  Moving ALL projects to {target_email}...")
        
        updated = 0
        for project in all_projects:
            result = await character_projects.update_one(
                {"_id": project["_id"]},
                {"$set": {"user_id": target_user_id}}
            )
            if result.modified_count > 0:
                updated += 1
        
        print(f"✅ Updated {updated} projects")
    
    elif choice == "2":
        dummy_names = ["food1", "bvcx", "ro4", "rohan", "rohan2", "rohan3"]
        dummy_projects = [p for p in all_projects if p.get("project_name") in dummy_names]
        
        if dummy_projects:
            print(f"\n⚠️  About to DELETE {len(dummy_projects)} projects:")
            for p in dummy_projects:
                print(f"   - {p.get('project_name')}")
            
            confirm = input("\nProceed? (yes/no): ")
            if confirm.lower() == "yes":
                deleted = 0
                for p in dummy_projects:
                    result = await character_projects.delete_one({"_id": p["_id"]})
                    if result.deleted_count > 0:
                        deleted += 1
                print(f"✅ Deleted {deleted} projects")
        else:
            print("No dummy projects found!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_and_fix_user_projects())
