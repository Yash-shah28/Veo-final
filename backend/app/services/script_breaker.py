from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from app.config import settings
import json


class SceneBreakdown(BaseModel):
    """Model for a single scene in the story"""
    scene_number: int = Field(description="The sequential number of the scene")
    description: str = Field(description="Detailed description of what happens in this scene")
    duration: int = Field(description="Duration of the scene in seconds (typically 8)")
    characters: List[str] = Field(description="List of character roles involved in this scene")
    visual_description: str = Field(description="Visual elements and setting of the scene")
    key_actions: str = Field(description="Main actions or events in the scene")

class StoryScenes(BaseModel):
    """Model for the complete story breakdown"""
    scenes: List[SceneBreakdown] = Field(description="List of all scenes in the story")
    total_scenes: int = Field(description="Total number of scenes")
    story_summary: str = Field(description="Brief summary of the overall story")

class ScriptBreaker:
    """Service class for breaking scripts into scenes using LangChain and Gemini"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured in settings")

        
        # Initialize Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            max_output_tokens=4096
        )
        
        # Setup output parser
        self.parser = PydanticOutputParser(pydantic_object=StoryScenes)
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert video production assistant specializing in breaking down stories into optimal video scenes.
            
Your task is to analyze the given script and break it into multiple scenes, where each scene:
- Should be approximately 8 seconds long when read aloud
- Contains a clear visual moment or action
- Has a specific setting and characters
- Can be effectively visualized in a single AI-generated video clip

Guidelines:
1. Each scene should be a complete visual moment
2. Identify which characters appear in each scene
3. Provide clear visual descriptions for AI video generation
4. Keep scenes concise and focused (8 seconds target)
5. Maintain story flow and continuity
6. Extract key actions that can be visualized

{format_instructions}
"""),
            ("user", """Please break down the following script into scenes:

SCRIPT:
{script}

Remember to create scenes that are:
- Approximately 8 seconds each
- Visually distinct and clear
- Include character involvement
- Have detailed visual descriptions for AI generation
""")
        ])
    
    async def break_script(self, script: str) -> dict:
        """
        Break a script into scenes using Gemini AI
        
        Args:
            script: The full story script to break down
            
        Returns:
            Dictionary containing scenes and metadata
        """
        try:
            # Format the prompt with script and parser instructions
            formatted_prompt = self.prompt.format_messages(
                script=script,
                format_instructions=self.parser.get_format_instructions()
            )
            
            # Get response from Gemini
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Parse the response
            parsed_result = self.parser.parse(response.content)
            
            # Convert to dictionary
            result = {
                "scenes": [scene.dict() for scene in parsed_result.scenes],
                "total_scenes": parsed_result.total_scenes,
                "story_summary": parsed_result.story_summary
            }
            
            return result
            
        except Exception as e:
            print(f"Error breaking script: {str(e)}")
            # Fallback to simple sentence-based breaking
            return self._fallback_script_breaking(script)
    
    def _fallback_script_breaking(self, script: str) -> dict:
        """
        Fallback method if AI fails - simple sentence-based breaking
        
        Args:
            script: The script to break down
            
        Returns:
            Dictionary with basic scene breakdown
        """
        # Split by sentences and group them
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        
        scenes = []
        for i, sentence in enumerate(sentences[:10], 1):  # Limit to 10 scenes
            scenes.append({
                "scene_number": i,
                "description": sentence,
                "duration": 8,
                "characters": ["protagonist"],  # Default character
                "visual_description": f"Scene showing: {sentence[:100]}",
                "key_actions": "Character narrating the story"
            })
        
        return {
            "scenes": scenes,
            "total_scenes": len(scenes),
            "story_summary": script[:200] if len(script) > 200 else script
        }

# Singleton instance
script_breaker = ScriptBreaker()
