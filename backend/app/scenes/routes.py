from fastapi import APIRouter
from typing import List
from app.database import db
from app.scenes.models import Scene, SceneCreate

router = APIRouter()

@router.post("/", response_model=Scene)
async def create_scene(scene: SceneCreate):
    scene_dict = scene.dict()
    new_scene = await db.scenes.insert_one(scene_dict)
    created_scene = await db.scenes.find_one({"_id": new_scene.inserted_id})
    return Scene(**created_scene)

@router.get("/", response_model=List[Scene])
async def read_scenes():
    scenes = await db.scenes.find().to_list(1000)
    return [Scene(**scene) for scene in scenes]
