# app/character/service.py - DISPATCHER SERVICE
# Routes to food or educational character services

from typing import Dict

# ========================================
# SHARED VOICE DESCRIPTIONS WITH MASTER PROMPTS
# ========================================
VOICE_DESCRIPTIONS = {
    "child_happy": {
        "description": "Cute, cheerful youthful voice",
        "pitch": "High",
        "age_range": "youthful",
        "accent": "neutral Indian accent",
        "vocal_tone": "bright, high-pitched voice",
        "speaking_style": "playful and energetic tone",
        "emotional_baseline": "speaks with innocent enthusiasm",
        "characteristics": "Youthful, clear pronunciation",
        "anchor_block": "A youthful character with a bright, high-pitched voice, playful and energetic tone, clear pronunciation, speaks with innocent enthusiasm.",
        "master_voice_prompt": "Youthful, bright voice, playful and cheerful tone, clear high-pitched delivery, energetic, clean audio."
    },
    "child_excited": {
        "description": "Energetic, bouncy youthful voice",
        "pitch": "Very high",
        "age_range": "youthful",
        "accent": "neutral Indian accent",
        "vocal_tone": "very high, animated voice",
        "speaking_style": "fast-paced and bouncy tone",
        "emotional_baseline": "speaks with bubbling excitement",
        "characteristics": "Youthful, eager delivery",
        "anchor_block": "A youthful character with a very high, animated voice, fast-paced and bouncy tone, eager delivery, speaks with bubbling excitement.",
        "master_voice_prompt": "Animated, excited voice, high-pitched and fast-paced, bouncy energetic tone, enthusiastic delivery, clean audio."
    },
    "male_friendly": {
        "description": "Friendly, warm adult male voice",
        "pitch": "Medium",
        "age_range": "late 20s to early 40s",
        "accent": "neutral Indian accent",
        "vocal_tone": "warm, friendly voice",
        "speaking_style": "approachable and clear tone",
        "emotional_baseline": "speaks with friendly confidence",
        "characteristics": "Approachable, clear, professional",
        "anchor_block": "A character in their late 20s to early 40s, with a warm, friendly voice, approachable and clear tone, neutral Indian accent, speaks with friendly confidence.",
        "master_voice_prompt": "Warm, clear male voice, calm and friendly tone, natural conversational delivery, neutral Indian accent, clean audio."
    },
    "male_strong": {
        "description": "Deep, mature adult male voice with clear delivery",
        "pitch": "Low to medium-low",
        "age_range": "late 30s to early 40s",
        "accent": "neutral Indian accent",
        "vocal_tone": "deep, warm voice",
        "speaking_style": "calm and measured tone",
        "emotional_baseline": "speaks with quiet confidence",
        "characteristics": "Confident, professional, authoritative",
        "anchor_block": "A character in their late 30s to early 40s, with a deep, warm voice, calm and measured tone, neutral Indian accent, speaks with quiet confidence.",
        "master_voice_prompt": "Deep, calm male voice, confident and professional tone, clear articulation, steady pace, neutral Indian accent, clean audio."
    },
    "adult_male": {
        "description": "Deep, mature adult male voice with clear delivery",
        "pitch": "Low to medium-low",
        "age_range": "late 30s to early 40s",
        "accent": "neutral Indian accent",
        "vocal_tone": "deep, warm voice",
        "speaking_style": "calm and measured tone",
        "emotional_baseline": "speaks with quiet confidence",
        "characteristics": "Confident, professional, authoritative",
        "anchor_block": "A character in their late 30s to early 40s, with a deep, warm voice, calm and measured tone, neutral Indian accent, speaks with quiet confidence.",
        "adult_male": {
        "description": "Professional adult male voice",
        "anchor_block": "A mature male with a clear and composed voice.",
        "master_voice_prompt": "Clear adult male voice, calm and professional, smooth delivery, easy to understand, clean indoor audio."
    },
    },
    "female_friendly": {
        "description": "Warm, mature adult female voice with friendly tone",
        "pitch": "Medium",
        "age_range": "early 30s to mid 40s",
        "accent": "neutral Indian accent",
        "vocal_tone": "warm, clear voice",
        "speaking_style": "friendly and approachable tone",
        "emotional_baseline": "speaks with gentle warmth",
        "characteristics": "Clear, approachable, professional",
        "anchor_block": "A character in their early 30s to mid 40s, with a warm, clear voice, friendly and approachable tone, neutral Indian accent, speaks with gentle warmth.",
        "master_voice_prompt": "Warm, clear female voice, friendly and gentle tone, natural pacing, neutral Indian accent, clean audio."
    },
    "adult_female": {
        "description": "Warm, mature adult female voice with friendly tone",
        "pitch": "Medium",
        "age_range": "early 30s to mid 40s",
        "accent": "neutral Indian accent",
        "vocal_tone": "warm, clear voice",
        "speaking_style": "friendly and approachable tone",
        "emotional_baseline": "speaks with gentle warmth",
        "characteristics": "Clear, approachable, professional",
        "anchor_block": "A character in their early 30s to mid 40s, with a warm, clear voice, friendly and approachable tone, neutral Indian accent, speaks with gentle warmth.",
       "master_voice_prompt": "Clear female voice, calm and professional delivery, smooth articulation, natural tone, clean indoor audio."
    },
    "female_soft": {
        "description": "Soft, gentle female voice, soothing tone",
        "pitch": "Medium-high",
        "age_range": "mid 20s to mid 30s",
        "accent": "soft Indian accent",
        "vocal_tone": "gentle, soothing voice",
        "speaking_style": "soft and reassuring tone",
        "emotional_baseline": "speaks with gentle grace",
        "characteristics": "Gentle, soothing, calm",
        "anchor_block": "A character in their mid 20s to mid 30s, with a soft, soothing voice, gentle tone, neutral Indian accent, speaks with quiet grace.",
       "master_voice_prompt": "Soft, calm female voice, slow and reassuring tone, gentle delivery, clean quiet audio."
    },
    "cartoon": {
        "description": "Expressive, animated cartoon character voice",
        "pitch": "Variable, expressive",
        "age_range": "ageless",
        "accent": "animated, clear",
        "vocal_tone": "bright, colorful voice",
        "speaking_style": "expressive and dynamic",
        "emotional_baseline": "speaks with character",
        "characteristics": "Fun, distinct, exaggerated",
        "anchor_block": "An animated character with a bright, expressive voice, dynamic tone, clear pronunciation, speaks with colorful personality.",
        "master_voice_prompt": "Fun, animated cartoon voice, expressive and energetic, playful tone, clear speech, lively delivery."
    },
}


class CharacterDialogueGenerator:
    """
    Dispatcher service that routes requests to:
    - food_character_service.py for food characters
    - educational_character_service.py for educational content
    """
    
    def __init__(self):
        pass
    
    async def generate_character_dialogue(
        self,
        character_name: str,
        content_type: str,  # "food" or "educational"
        voice_tone: str,
        custom_voice_description: str = None,  # NEW: Custom voice support
        topic_mode: str = "",
        scenario: str = "",
        visual_style: str = "Realistic Character",
        language: str = "hindi",
        total_duration: int = 8,
        custom_dialogues: str = None  # NEW: Custom dialogues for food
    ) -> Dict:
        """
        Dispatcher: Routes to food or educational character service
        """
        print(f"\n{'='*60}")
        print(f"🎯 DISPATCHER: Routing to {content_type} service")
        print(f"{'='*60}")
        
        # Import services
        from app.character.food_character_service import food_character_generator
        from app.character.educational_character_service import educational_character_generator
        
        # Route based on content type
        if content_type == "food":
            return await food_character_generator.generate_dialogue(
                character_name=character_name,
                voice_tone=voice_tone,
                topic_mode=topic_mode,
                scenario=scenario,
                visual_style=visual_style,
                language=language,
                total_duration=total_duration,
                custom_dialogues=custom_dialogues  # NEW: Pass custom dialogues
            )
        else:  # educational
            return await educational_character_generator.generate_dialogue(
                character_name=character_name,
                voice_tone=voice_tone,
                custom_voice_description=custom_voice_description,  # NEW: Pass custom voice
                scenario=scenario,
                visual_style=visual_style,
                language=language,
                total_duration=total_duration
            )


# Create singleton instance
character_dialogue_generator = CharacterDialogueGenerator()