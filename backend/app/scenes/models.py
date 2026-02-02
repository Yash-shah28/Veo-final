from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Annotated
from bson import ObjectId

# Helper to map ObjectId to str
PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x) if x is not None else None)]

class SceneBase(BaseModel):
    title: str
    description: Optional[str] = None
    script: Optional[str] = None

class SceneCreate(SceneBase):
    pass

class Scene(SceneBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    owner_id: Optional[PyObjectId] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
