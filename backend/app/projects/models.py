from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId

# Helper to map ObjectId to str
PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x) if x is not None else None)]

class ProjectBase(BaseModel):
    project_name: str
    project_type: str  # "storytelling" | "character" | "ugc"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    characters: Optional[Dict[str, Any]] = None

class Project(ProjectBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    characters: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    raw_script: Optional[str] = None
    script_broken: bool = False
    total_scenes: int = 0

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ProjectListItem(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    project_name: str
    project_type: str
    created_at: datetime
    total_scenes: int

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
