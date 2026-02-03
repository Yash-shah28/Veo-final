from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import db
from app.projects.models import Project, ProjectCreate, ProjectUpdate, ProjectListItem
from app.users.models import User
from app.auth.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from app.services.script_breaker import script_breaker

router = APIRouter()

# Request model for script breaking
class ScriptBreakRequest(BaseModel):
    script: str


@router.get("/", response_model=List[ProjectListItem])
async def get_user_projects(current_user: User = Depends(get_current_user)):
    """Get all projects for the current user"""
    try:
        projects = await db.projects.find(
            {"user_id": ObjectId(current_user.id)}
        ).sort("created_at", -1).to_list(100)
        
        return [ProjectListItem(**project) for project in projects]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    try:
        project_dict = project.model_dump()
        project_dict["user_id"] = ObjectId(current_user.id)
        project_dict["created_at"] = datetime.utcnow()
        project_dict["last_updated"] = datetime.utcnow()
        project_dict["characters"] = {}
        project_dict["settings"] = {
            "visual_style": "Cinematic Photorealism",
            "default_duration": 8
        }
        project_dict["total_scenes"] = 0
        project_dict["script_broken"] = False
        
        result = await db.projects.insert_one(project_dict)
        created_project = await db.projects.find_one({"_id": result.inserted_id})
        
        return Project(**created_project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific project by ID"""
    try:
        project = await db.projects.find_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(current_user.id)
        })
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return Project(**project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project: {str(e)}"
        )

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a project"""
    try:
        # Check if project exists and belongs to user
        existing_project = await db.projects.find_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(current_user.id)
        })
        
        if not existing_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Build update dict
        update_data = {k: v for k, v in project_update.model_dump(exclude_unset=True).items()}
        if update_data:
            update_data["last_updated"] = datetime.utcnow()
            
            await db.projects.update_one(
                {"_id": ObjectId(project_id)},
                {"$set": update_data}
            )
        
        updated_project = await db.projects.find_one({"_id": ObjectId(project_id)})
        return Project(**updated_project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a project and all its scenes"""
    try:
        # Check if project exists and belongs to user
        project = await db.projects.find_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(current_user.id)
        })
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Delete all scenes for this project
        await db.scenes.delete_many({"project_id": ObjectId(project_id)})
        
        # Delete the project
        await db.projects.delete_one({"_id": ObjectId(project_id)})
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

@router.post("/{project_id}/break-script")
async def break_script(
    project_id: str,
    request: ScriptBreakRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Break a script into scenes using AI
    
    This endpoint uses LangChain with Gemini to intelligently break down
    a story script into optimal 8-second video scenes.
    """
    try:
        # Verify project exists and belongs to user
        project = await db.projects.find_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(current_user.id)
        })
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Validate script
        if not request.script or not request.script.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Script cannot be empty"
            )
        
        # Break script using AI
        try:
            result = await script_breaker.break_script(request.script)
        except Exception as ai_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI processing failed: {str(ai_error)}"
            )
        
        # 1. Delete existing scenes for this project (clean slate)
        await db.scenes.delete_many({"project_id": ObjectId(project_id)})

        # 2. Prepare new scenes for batch insertion
        new_scenes = []
        for scene_data in result["scenes"]:
            scene_doc = scene_data.copy()
            scene_doc["project_id"] = ObjectId(project_id)
            scene_doc["user_id"] = ObjectId(current_user.id)
            scene_doc["created_at"] = datetime.utcnow()
            scene_doc["updated_at"] = datetime.utcnow()
            scene_doc["characters_in_scene"] = {} # Initialize empty map for consistency
            
            # Map AI fields to DB schema if needed
            if "visual_description" in scene_doc:
                scene_doc["generated_prompt"] = scene_doc.pop("visual_description")
            
            new_scenes.append(scene_doc)
            
        if new_scenes:
            await db.scenes.insert_many(new_scenes)

        # Update project with script and scene count
        update_data = {
            "raw_script": request.script,
            "script_broken": True,
            "total_scenes": result["total_scenes"],
            "last_updated": datetime.utcnow()
        }
        
        await db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": update_data}
        )
        
        # Fetch the created scenes to return them with IDs
        created_scenes = await db.scenes.find(
            {"project_id": ObjectId(project_id)}
        ).sort("scene_number", 1).to_list(100)
        
        return {
            "success": True,
            "project_id": project_id,
            "scenes": [
                {**scene, "_id": str(scene["_id"]), "project_id": str(scene["project_id"]), "user_id": str(scene["user_id"])} 
                for scene in created_scenes
            ],
            "total_scenes": result["total_scenes"],
            "story_summary": result.get("story_summary", ""),
            "message": f"Successfully broke script into {result['total_scenes']} scenes and saved to database"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to break script: {str(e)}"
        )

class CharacterRequest(BaseModel):
    role: str
    name: str
    description: str | None = None
    voice_type: str | None = None
    voice_tone: str | None = None
    image_base64: str | None = None

@router.post("/{project_id}/characters")
async def add_project_character(
    project_id: str,
    character: CharacterRequest,
    current_user: User = Depends(get_current_user)
):
    """Add a new character to the project"""
    try:
        # Verify project existence
        project = await db.projects.find_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(current_user.id)
        })
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
            
        # Create character object
        char_data = {
            "name": character.name,
            "base_description": character.description,
            "voice_type": character.voice_type,
            "voice_tone": character.voice_tone,
            "image_base64": character.image_base64,
            "added_at": datetime.utcnow()
        }
        
        # Normalize role key (e.g., "Supporting 1" -> "supporting_1")
        role_key = character.role.lower().replace(" ", "_")
        
        # Update project using MongoDB dot notation for nested objects
        await db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                f"characters.{role_key}": char_data,
                "last_updated": datetime.utcnow()
            }}
        )
        
        return {
            "success": True, 
            "message": f"Character '{character.name}' added as {character.role}",
            "character": {
                "role": role_key,
                **char_data
            }
        }
        
        return {
            "success": True, 
            "message": f"Character '{character.name}' added as {character.role}",
            "character": {
                "role": role_key,
                **char_data
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add character: {str(e)}"
        )

@router.get("/{project_id}/scenes")
async def get_project_scenes(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all scenes for a specific project"""
    try:
        # Verify project existence
        project = await db.projects.find_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(current_user.id)
        })
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
            
        scenes = await db.scenes.find(
            {"project_id": ObjectId(project_id)}
        ).sort("scene_number", 1).to_list(1000)
        
        # Convert ObjectId to str for response
        return [
            {**scene, "_id": str(scene["_id"]), "project_id": str(scene["project_id"]), "user_id": str(scene["user_id"])} 
            for scene in scenes
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch scenes: {str(e)}"
        )



