from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId

# Helper to map ObjectId to str
PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x) if x is not None else None)]

class CharacterOverride(BaseModel):
    emotion: Optional[str] = None
    costume: Optional[str] = None
    dialogue: Optional[str] = None
    action: Optional[str] = None

class SceneBase(BaseModel):
    scene_number: int
    description: str
    duration: int = 8
    scene_type: str = "dialogue"  # "dialogue" | "scene_change" | "action"
    characters_in_scene: Dict[str, CharacterOverride] = {}
    story_context: Optional[str] = None
    generated_prompt: Optional[str] = None
    visual_description: Optional[str] = None
    key_actions: Optional[str] = None

class SceneCreate(SceneBase):
    pass

class Scene(SceneBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    project_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

