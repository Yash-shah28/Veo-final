from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import db
from app.projects.models import Project, ProjectCreate, ProjectUpdate, ProjectListItem
from app.users.models import User
from app.auth.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()

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
