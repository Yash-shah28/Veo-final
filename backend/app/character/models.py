from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class CharacterSceneRequest(BaseModel):
    """Request model for generating character dialogue"""
    character_name: str = Field(..., description="Name of the character (e.g., Apple, Carrot)")
    voice_tone: str = Field(..., description="Voice tone/type")
    topic_mode: str = Field(..., description="benefits or side_effects")
    scenario: Optional[str] = Field(None, description="Context/scenario for the character")
    visual_style: str = Field(default="3D Animation (Pixar/Disney) - Best")
    language: str = Field(default="hindi", description="hindi or english")
    total_duration: int = Field(default=8, description="Total video duration in seconds")
    project_id: Optional[str] = Field(None, description="Associated project ID")

class CharacterScene(BaseModel):
    """Model for a single character scene (8 seconds) with detailed Veo format"""
    scene_number: int = Field(description="Scene number in sequence")
    visual_prompt: str = Field(description="Detailed visual description for Veo")
    dialogue: str = Field(description="Character dialogue in specified language")
    emotion: str = Field(description="Character emotion/expression")
    teaching_point: str = Field(description="Educational point being made")
    
    # Scene Metadata
    duration: int = Field(default=8, description="Scene duration in seconds")
    aspect_ratio: str = Field(default="9:16", description="Video aspect ratio")
    
    # Audio Style
    voice_type: str = Field(description="Voice description (e.g., Deep male, Soft female)")
    voice_emotion: str = Field(description="Voice emotion (e.g., angry, happy, calm)")
    background_audio: str = Field(description="Background audio description")
    
    # Lip Sync Data
    lip_sync_text: str = Field(description="Text for lip sync")
    speaker_id: str = Field(description="Speaker identifier")
    
    # Complete formatted prompt
    prompt: str = Field(description="Complete formatted prompt with all sections")

class CharacterDialogueResponse(BaseModel):
    """Response model with broken down scenes"""
    scenes: List[CharacterScene] = Field(description="List of 8-second character scenes")
    total_scenes: int = Field(description="Total number of scenes")
    character_name: str = Field(description="Character name")
    topic: str = Field(description="Topic being discussed")

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class CharacterProjectDB(BaseModel):
    """Database model for character mode project"""
    user_id: str
    project_name: str
    project_type: str = "character"
    character_name: str
    voice_tone: str
    topic_mode: str
    scenario: Optional[str]
    visual_style: str
    language: str
    total_duration: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CharacterSceneDB(BaseModel):
    """Database model for individual character scene"""
    project_id: str
    user_id: str
    scene_number: int
    dialogue: str
    emotion: str
    teaching_point: str
    generated_prompt: str
    duration: int = 8
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
