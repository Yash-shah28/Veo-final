from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.character.models import (
    CharacterSceneRequest,
    CharacterDialogueResponse,
    CharacterScene,
    CharacterProjectDB,
    CharacterSceneDB
)
from app.character.service import character_dialogue_generator
from app.auth.dependencies import get_current_user
from app.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/generate-character-dialogue")
async def generate_character_dialogue(
    request: CharacterSceneRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate talking character dialogue broken into 8-second scenes
    
    This endpoint:
    1. Takes character details and total duration
    2. Uses Gemini AI to generate educational dialogue
    3. Breaks it into 8-second scenes automatically
    4. Returns all scenes with complete Veo prompts
    """
    try:
        # Generate dialogue using Gemini
        result = await character_dialogue_generator.generate_character_dialogue(
            character_name=request.character_name,
            voice_tone=request.voice_tone,
            topic_mode=request.topic_mode,
            scenario=request.scenario or "",
            visual_style=request.visual_style,
            language=request.language,
            total_duration=request.total_duration
        )
        
        # Always save to database (create new project if project_id not provided)
        try:
            # Generate new project_id if not provided
            project_id = request.project_id
            user_id = str(current_user.id)
            if not project_id:
                # Create new project
                project_doc = {
                    "user_id": user_id,
                    "project_name": f"{request.character_name} - {request.topic_mode}",
                    "character_name": request.character_name,
                    "voice_tone": request.voice_tone,
                    "topic_mode": request.topic_mode,
                    "scenario": request.scenario,
                    "visual_style": request.visual_style,
                    "language": request.language,
                    "total_duration": request.total_duration,
                    "created_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow()
                }
                insert_result = await db.character_projects.insert_one(project_doc)
                project_id = str(insert_result.inserted_id)
            else:
                # Update existing project
                project_data = CharacterProjectDB(
                    user_id=user_id,
                    project_name=f"{request.character_name} - {request.topic_mode}",
                    character_name=request.character_name,
                    voice_tone=request.voice_tone,
                    topic_mode=request.topic_mode,
                    scenario=request.scenario,
                    visual_style=request.visual_style,
                    language=request.language,
                    total_duration=request.total_duration,
                    last_updated=datetime.utcnow()
                )
                
                await db.character_projects.update_one(
                    {"_id": ObjectId(project_id)},
                    {"$set": project_data.dict()},
                    upsert=True
                )
            
            # Save individual scenes
            for scene_data in result["scenes"]:
                scene_db = CharacterSceneDB(
                    project_id=project_id,
                    user_id=user_id,
                    scene_number=scene_data["scene_number"],
                    dialogue=scene_data["dialogue"],
                    emotion=scene_data["emotion"],
                    teaching_point=scene_data["teaching_point"],
                    generated_prompt=scene_data["prompt"],
                    updated_at=datetime.utcnow()
                )
                
                # Upsert scene
                await db.character_scenes.update_one(
                    {
                        "project_id": project_id,
                        "scene_number": scene_data["scene_number"]
                    },
                    {"$set": scene_db.dict()},
                    upsert=True
                )
            
            # Add project_id to response
            result["project_id"] = project_id
            result["message"] = "Scenes generated and saved successfully"
            
        except Exception as db_error:
                print(f"Database save error: {str(db_error)}")
                # Continue even if DB save fails
        
        # Return result directly as dict (no Pydantic validation)
        return result
        
    except Exception as e:
        import traceback
        print(f"❌ Route Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate character dialogue: {str(e)}"
        )

@router.get("/projects/{project_id}/scenes")
async def get_character_project_scenes(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all scenes for a character project"""
    try:
        # Convert current_user to dict for easier access
        user_id = str(current_user.id)
        print(f"🔍 Loading project: {project_id} for user: {user_id}")
        
        # Verify project belongs to user
        project = await db.character_projects.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        
        print(f"📦 Project found: {project is not None}")
        
        if not project:
            print(f"❌ Project not found: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get all scenes
        scenes = await db.character_scenes.find({
            "project_id": project_id
        }).sort("scene_number", 1).to_list(100)
        
        print(f"🎬 Found {len(scenes)} scenes")
        
        # Convert ObjectId to string
        for scene in scenes:
            scene["_id"] = str(scene["_id"])
        
        result = {
            "project": {
                "_id": str(project["_id"]),
                "project_name": project.get("project_name", "Untitled"),
                "character_name": project.get("character_name", ""),
                "total_duration": project.get("total_duration", 0)
            },
            "scenes": scenes
        }
        
        print(f"✅ Returning {len(scenes)} scenes for project")
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        print(f"❌ ERROR in get_character_project_scenes: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch scenes: {str(e)}"
        )

@router.post("/projects")
async def create_character_project(
    project_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new character project"""
    try:
        user_id = str(current_user.id)
        project = CharacterProjectDB(
            user_id=user_id,
            **project_data
        )
        
        result = await db.character_projects.insert_one(project.dict())
        
        return {
            "project_id": str(result.inserted_id),
            "message": "Character project created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/projects")
async def get_user_character_projects(
    current_user: dict = Depends(get_current_user)
):
    """Get all character projects for the current user"""
    try:
        user_id = str(current_user.id)
        print(f"🔍 Fetching projects for user: {user_id}")
        
        projects = await db.character_projects.find({
            "user_id": user_id
        }).sort("last_updated", -1).to_list(100)
        
        print(f"📦 Found {len(projects)} character projects")
        for p in projects:
            print(f"  - {p.get('project_name')} (ID: {p.get('_id')})")
        
        # Convert ObjectId to string
        for project in projects:
            project["_id"] = str(project["_id"])
            project["created_at"] = project["created_at"].isoformat()
            project["last_updated"] = project["last_updated"].isoformat()
        
        return {"projects": projects}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )
