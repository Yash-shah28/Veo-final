# app/character/service.py - PROPER VISUAL PROMPTS + HINGLISH + OUTFIT EXTRACTION

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict
from app.config import settings
import re
import json

# ========================================
# VOICE MAPPING WITH VEO 3 ANCHORS
# ========================================
VOICE_DESCRIPTIONS = {
    "adult_male": {
        "description": "Deep, mature adult male voice with clear delivery",
        "pitch": "Low to medium-low",
        "age_range": "late 30s to early 40s",
        "characteristics": "Confident, professional, authoritative",
        "anchor_block": "A character in their late 30s to early 40s, with a deep, warm voice, calm and measured tone, neutral Indian accent, speaks with quiet confidence.",
        "audio_descriptor": "Close-mic, clean audio, no reverb"
    },
    "adult_female": {
        "description": "Warm, mature adult female voice with friendly tone",
        "pitch": "Medium",
        "age_range": "early 30s to mid 40s",
        "characteristics": "Clear, approachable, professional",
        "anchor_block": "A character in their late 30s to early 40s, with a deep, warm voice, calm and measured tone, neutral Indian accent, speaks with quiet confidence.",
        "audio_descriptor": "Close-mic, clean audio, no reverb"
    },
    "female_friendly": {
        "description": "Warm, mature adult female voice with friendly tone",
        "pitch": "Medium",
        "age_range": "early 30s to mid 40s",
        "characteristics": "Clear, approachable, professional",
        "anchor_block": "A character in their early 30s to mid 40s, with a warm, clear voice, friendly and approachable tone, neutral Indian accent, speaks with gentle warmth.",
        "audio_descriptor": "Close-mic, clean audio, no reverb"
    },
    "child_happy": {
        "description": "Cute, cheerful child voice (3-5 years old)",
        "pitch": "High, bright",
        "age_range": "3 to 5 years old",
        "characteristics": "Playful, innocent, enthusiastic",
        "anchor_block": "A child character, 3 to 5 years old, with a bright, high-pitched voice, playful and energetic tone, childlike clear pronunciation, speaks with innocent enthusiasm.",
        "audio_descriptor": "Close-mic, clean audio, slight brightness"
    },
    "child_excited": {
        "description": "Energetic, bouncy child voice (3-5 years old)",
        "pitch": "Very high, excited",
        "age_range": "3 to 5 years old",
        "characteristics": "Fast-paced, eager, animated",
        "anchor_block": "A child character, 3 to 5 years old, with a very high, animated voice, fast-paced and bouncy tone, childlike eager delivery, speaks with bubbling excitement.",
        "audio_descriptor": "Close-mic, clean audio, energetic"
    },
    "baby_cute": {
        "description": "Adorable baby voice (1-2 years old)",
        "pitch": "Very high, baby-like",
        "age_range": "1 to 2 years old",
        "characteristics": "Cooing, giggly, sweet",
        "anchor_block": "A baby character, 1 to 2 years old, with a very high, sweet voice, gentle and cooing tone, baby babbling with simple sounds, speaks with adorable innocence.",
        "audio_descriptor": "Close-mic, soft audio, gentle"
    },
    "baby_crying": {
        "description": "Crying baby voice (1-2 years old)",
        "pitch": "High, distressed",
        "age_range": "1 to 2 years old",
        "characteristics": "Crying, whimpering, upset",
        "anchor_block": "A baby character, 1 to 2 years old, with a high, whimpering voice, upset and crying tone, baby crying with distressed sounds, speaks with visible distress.",
        "audio_descriptor": "Close-mic, emotional audio, slight reverb"
    },
    "energetic": {
        "description": "Super energetic, motivating voice",
        "pitch": "Medium-high",
        "age_range": "mid 20s to early 30s",
        "characteristics": "Enthusiastic, inspiring, upbeat",
        "anchor_block": "A character in their mid 20s to early 30s, with a bright, enthusiastic voice, energetic and inspiring tone, neutral Indian accent, speaks with motivating enthusiasm.",
        "audio_descriptor": "Close-mic, crisp audio, upbeat"
    },
    "calm": {
        "description": "Calm, gentle, soothing voice",
        "pitch": "Medium-low",
        "age_range": "mid 30s to mid 40s",
        "characteristics": "Relaxing, reassuring, peaceful",
        "anchor_block": "A character in their mid 30s to mid 40s, with a soft, soothing voice, calm and gentle tone, neutral Indian accent, speaks with peaceful reassurance.",
        "audio_descriptor": "Close-mic, warm audio, slight room tone"
    },
}


class CharacterDialogueGenerator:
    """Generate educational character dialogues"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            max_output_tokens=4096
        )
    
    async def _detect_character_type(self, character_name: str, topic_mode: str, scenario: str) -> Dict:
        """Detect if food or educational character"""
        
        if scenario and len(scenario.strip()) > 50:
            return {"type": "educational", "reason": "Detailed scenario"}
        
        if topic_mode in ["benefits", "side_effects"]:
            detection_prompt = f"""Is "{character_name}" a FOOD, FRUIT, VEGETABLE, or EDIBLE ITEM?

Answer ONLY "FOOD" or "NOT_FOOD"

Examples:
- "apple" → FOOD
- "rohan" → NOT_FOOD
- "chocolate" → FOOD

Character: "{character_name}"

Answer:"""

            try:
                messages = [("user", detection_prompt)]
                prompt_template = ChatPromptTemplate.from_messages(messages)
                chain = prompt_template | self.llm
                
                response = await chain.ainvoke({})
                result = response.content.strip().upper()
                
                if "FOOD" in result and "NOT" not in result:
                    return {"type": "food", "reason": f"{character_name} is food"}
                else:
                    return {"type": "educational", "reason": f"{character_name} not food"}
                    
            except Exception as e:
                print(f"⚠️ Detection failed: {e}")
                return {"type": "educational", "reason": "Detection failed"}
        else:
            return {"type": "educational", "reason": "Non-health topic"}
    
    async def generate_character_dialogue(
        self,
        character_name: str,
        voice_tone: str,
        topic_mode: str,
        scenario: str,
        visual_style: str,
        language: str,
        total_duration: int
    ) -> Dict:
        """Generate dialogue with STRICT 7-second limits"""
        
        print(f"\n{'='*60}")
        print(f"🎬 GENERATING 7-SECOND SCENES")
        print(f"{'='*60}")
        print(f"Character: {character_name}")
        print(f"Voice: {voice_tone}")
        print(f"Topic: {topic_mode}")
        print(f"Language: {language}")
        print(f"Duration: {total_duration}s")
        
        # STEP 1: Detect type
        detection = await self._detect_character_type(character_name, topic_mode, scenario)
        character_type = detection["type"]
        
        print(f"🔍 Type: {character_type}")
        
        # STEP 2: Get voice info
        voice_info = VOICE_DESCRIPTIONS.get(voice_tone, VOICE_DESCRIPTIONS["adult_male"])
        
        voice_description = voice_info["description"]
        voice_pitch = voice_info["pitch"]
        voice_age_range = voice_info.get("age_range", "adult")
        voice_characteristics = voice_info["characteristics"]
        
        # VEO 3: Anchor & Audio
        voice_anchor = voice_info.get("anchor_block", voice_description)
        audio_descriptor = voice_info.get("audio_descriptor", "Close-mic, clean audio")
        
        print(f"✅ Voice: {voice_description}")
        print(f"🎤 Anchor: {voice_anchor[:50]}...")
        print(f"🔊 Audio: {audio_descriptor}")
        
        # STEP 3: Emotions
        if character_type == "food":
            if topic_mode == "side_effects":
                emotions = ["serious", "warning", "concerned", "cautious"] if "baby_crying" not in voice_tone else ["crying", "upset"]
            else:
                emotions = ["happy", "excited", "cheerful", "joyful"] if ("child" in voice_tone or "baby_cute" in voice_tone) else ["confident", "encouraging", "positive"]
        else:
            emotions = ["engaged", "explaining", "friendly", "clear"]
        
        # STEP 4: Calculate scenes
        num_scenes = max(1, total_duration // 8)
        
        print(f"📊 Scenes: {num_scenes}")
        
        # STEP 5: Build prompt - WITH HINGLISH
        lang_display = "HINGLISH (Hindi-English Mix)" if language == "hindi" else "ENGLISH"
        
        if character_type == "food":
            # FOOD MODE - STRICT 7-SECOND LIMITS WITH HINGLISH
            system_prompt = f"""Create {num_scenes} 7-SECOND video scenes about {character_name} ({topic_mode}).

VEO 3 VOICE ANCHOR (COPY EXACTLY):
{voice_anchor}

AUDIO DESCRIPTOR (ADD TO EVERY VISUAL PROMPT):
{audio_descriptor}

LANGUAGE: {lang_display}
🚨 USE NATURAL HINGLISH - Mix Hindi & English words naturally like normal conversation!

For each scene:
===SCENE X===
Visual Prompt (Veo 3 Format):
[Shot type - Medium shot/Close-up]. {voice_anchor}. {character_name} character [as animated food - describe shape, color, facial expression], looking [emotion], [action - pointing/gesturing/moving]. Says: [dialogue]. {audio_descriptor}. Background: [simple kitchen/nature setting]. No subtitles.

Dialogue ({lang_display}):
[Scene 1: Main {character_name} hoon + ONE fact - MAX 10 words TOTAL]
[Scene 2+: ONE fact - MAX 7 words]

Teaching Point:
[One fact]
===END SCENE X===

🚨 STRICT LIMITS (7 SECONDS) 🚨:
✅ Scene 1: MAX 10 words (including intro)
✅ Scene 2+: MAX 7 words ONLY
✅ ONE complete sentence per scene
✅ Voice Anchor "{voice_anchor}" in EVERY Visual Prompt
✅ Audio "{audio_descriptor}" in EVERY Visual Prompt after "Says:"

🗣️ HINGLISH STYLE (MANDATORY):
✅ Mix Hindi verbs + English nouns naturally
✅ Use simple everyday words everyone understands
✅ Technical terms in ENGLISH (Vitamin, Protein, Calcium, Iron, Fiber)
✅ Common words can be Hindi (main, hoon, mein, hai, ko, se)
✅ Sound like normal Indian conversation
✅ Write in ROMAN script (NOT Devanagari)

🎨 VISUAL DETAILS (MANDATORY):
✅ Describe food character appearance (round apple with face, orange carrot with smile)
✅ Include colors and features
✅ Specify action/gesture in each scene
✅ Use shot type (Medium shot/Close-up)

❌ FORBIDDEN:
❌ NO pure Devanagari/Sanskrit words
❌ NO formal Hindi like "रोग प्रतिरोधक क्षमता"
❌ NO "और", "तथा" to add extra info
❌ NO dialogue > word limits
❌ NO multiple sentences
❌ NO generic visuals like "Apple character" without description

EXAMPLES (CORRECT - HINGLISH 7 SECONDS):

===SCENE 1===
Visual Prompt (Veo 3 Format):
Medium shot. A character in their late 30s to early 40s, with a deep, warm voice, calm and measured tone, neutral Indian accent, speaks with quiet confidence. Red round Apple character with friendly face and leafy top, looking happy, waving cheerfully. Says: Main Apple hoon. Mujhme Vitamin C hai. Close-mic, clean audio, no reverb. Background: bright kitchen counter. No subtitles.

Dialogue (HINGLISH):
Main Apple hoon. Mujhme Vitamin C hai.

Teaching Point:
Apples contain Vitamin C

===SCENE 2===
Visual Prompt (Veo 3 Format):
Close-up. A character in their late 30s to early 40s, with a deep, warm voice, calm and measured tone, neutral Indian accent, speaks with quiet confidence. Red Apple character with big smile, looking confident, pointing at heart icon. Says: Heart ko healthy rakhta hoon. Close-mic, clean audio, no reverb. Background: soft green garden. No subtitles.

Dialogue (HINGLISH):
Heart ko healthy rakhta hoon.

Teaching Point:
Good for heart health

Generate {num_scenes} scenes in NATURAL HINGLISH with DETAILED visuals:"""

        else:
            # EDUCATIONAL MODE - STRICT 7-SECOND LIMITS WITH HINGLISH  
            content = scenario if scenario else f"Content about {topic_mode}"
            
            system_prompt = f"""Create {num_scenes} 7-SECOND scenes where {character_name} explains: {content}

VEO 3 VOICE ANCHOR (COPY EXACTLY):
{voice_anchor}

AUDIO DESCRIPTOR (ADD TO EVERY VISUAL PROMPT):
{audio_descriptor}

LANGUAGE: {lang_display}
🚨 USE NATURAL HINGLISH - Mix Hindi & English words naturally like normal conversation!

📋 SCENARIO PROVIDED: {content}
⚠️ CRITICAL: Extract character's outfit, clothing colors, and appearance details from the scenario above. Use these details in EVERY visual prompt!

For each scene:
===SCENE X===
Visual Prompt (Veo 3 Format):
[Shot type - Medium shot/Close-up/Wide shot]. {voice_anchor}. {character_name} character wearing [EXACT outfit from scenario - colors, style, items], looking [emotion], [specific teaching gesture - pointing, showing, explaining]. Says: [dialogue]. {audio_descriptor}. Background: [setting for topic - office/classroom/lab]. No subtitles.

Dialogue ({lang_display}):
[Scene 1: Brief intro + ONE point - MAX 15 words]
[Scene 2+: ONE point - MAX 20 words]

Teaching Point:
[Key point]
===END SCENE X===

🚨 STRICT LIMITS (7 SECONDS) 🚨:
✅ Scene 1: MAX 15 words (intro + one point)
✅ Scene 2+: MAX 12 words
✅ ONE complete thought per scene
✅ Voice Anchor in EVERY Visual Prompt
✅ Audio descriptor in EVERY Visual Prompt

🗣️ HINGLISH STYLE (MANDATORY):
✅ Mix Hindi verbs + English nouns naturally
✅ Use simple everyday words everyone understands
✅ Technical/scientific terms in ENGLISH (Photosynthesis, DNA, Gravity, Evolution)
✅ Common words can be Hindi (aaj, main, kya, hai, hota, karenge, mein, ko)
✅ Sound like a teacher talking to Indian students
✅ Write in ROMAN script (NOT Devanagari)

🎨 VISUAL DETAILS (MANDATORY):
✅ Extract and use outfit details from scenario (green suit, white shirt, etc.)
✅ Include character's physical appearance
✅ Specify teaching action (pointing, gesturing, showing diagram)
✅ Use appropriate shot type
✅ Add relevant background

❌ FORBIDDEN:
❌ NO pure Devanagari/Sanskrit words
❌ NO formal Hindi like "प्रकाश संश्लेषण"
❌ NO dialogue > word limits
❌ NO multiple sentences in one scene
❌ NO generic visuals without outfit/appearance details

EXAMPLES (CORRECT - HINGLISH with outfit details):

===SCENE 1===
Visual Prompt (Veo 3 Format):
Medium shot. A character in their late 30s to early 40s, with a deep, warm voice, calm and measured tone, neutral Indian accent, speaks with quiet confidence. Yagnesh Modh character wearing green suit and white shirt, looking engaged, gesturing welcomingly. Says: Aaj main bataunga AI videos kaise bante hain. Close-mic, clean audio, no reverb. Background: modern office with screens. No subtitles.

Dialogue (HINGLISH):
Aaj main bataunga AI videos kaise bante hain.

Teaching Point:
Introduction to AI video generation

===SCENE 2===
Visual Prompt (Veo 3 Format):
Close-up. A character in their late 30s to early 40s, with a deep, warm voice, calm and measured tone, neutral Indian accent, speaks with quiet confidence. Yagnesh Modh in green suit, looking explaining, pointing at floating text. Says: Characters change hote hain har regeneration mein. Close-mic, clean audio, no reverb. Background: tech workspace. No subtitles.

Dialogue (HINGLISH):
Characters change hote hain har regeneration mein.

Teaching Point:
AI characters vary with each generation

Generate {num_scenes} scenes in NATURAL HINGLISH with COMPLETE outfit details:"""
        
        # STEP 6: Call Gemini
        try:
            print(f"🤖 Calling Gemini...")
            
            messages = [("user", system_prompt)]
            prompt_template = ChatPromptTemplate.from_messages(messages)
            chain = prompt_template | self.llm
            
            response = await chain.ainvoke({})
            raw_output = response.content
            
            print(f"✅ Gemini: {len(raw_output)} chars")
            
        except Exception as e:
            error_msg = f"Gemini failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                "error": True,
                "message": error_msg,
                "scenes": [],
                "total_scenes": 0
            }
        
        # STEP 7: Parse output
        scenes = []
        
        scene_pattern = r'===SCENE (\d+)===(.*?)===END SCENE \1==='
        scene_blocks = re.findall(scene_pattern, raw_output, re.DOTALL | re.IGNORECASE)
        
        print(f"📝 Found {len(scene_blocks)} scenes")
        
        if len(scene_blocks) == 0:
            parts = re.split(r'===\s*SCENE\s+\d+\s*===', raw_output, flags=re.IGNORECASE)
            if len(parts) > 1:
                for idx, part in enumerate(parts[1:], 1):
                    visual_match = re.search(r'Visual Prompt:(.*?)(?=Dialogue|Teaching|$)', part, re.DOTALL | re.IGNORECASE)
                    visual = visual_match.group(1).strip() if visual_match else ""
                    
                    dialogue_match = re.search(r'Dialogue[^:]*:(.*?)(?=Teaching|$)', part, re.DOTALL | re.IGNORECASE)
                    dialogue = dialogue_match.group(1).strip() if dialogue_match else ""
                    
                    teaching_match = re.search(r'Teaching Point:(.*?)$', part, re.DOTALL | re.IGNORECASE)
                    teaching = teaching_match.group(1).strip() if teaching_match else ""
                    
                    if visual or dialogue:
                        scene_blocks.append((str(idx), f"\nVisual Prompt:\n{visual}\n\nDialogue:\n{dialogue}\n\nTeaching Point:\n{teaching}\n"))
        
        if len(scene_blocks) == 0:
            return {
                "error": True,
                "message": "Failed to parse output",
                "scenes": [],
                "total_scenes": 0,
                "debug_output": raw_output[:1000]
            }
        
        # Build scenes
        for idx, (scene_num_str, scene_content) in enumerate(scene_blocks):
            scene_num = int(scene_num_str)
            
            visual_match = re.search(r'Visual Prompt:(.*?)(?=Dialogue|Teaching|$)', scene_content, re.DOTALL | re.IGNORECASE)
            visual_prompt = visual_match.group(1).strip() if visual_match else f"{character_name} character"
            
            dialogue_match = re.search(r'Dialogue[^:]*:(.*?)(?=Teaching|$)', scene_content, re.DOTALL | re.IGNORECASE)
            dialogue = dialogue_match.group(1).strip().strip('"\'') if dialogue_match else ""
            
            teaching_match = re.search(r'Teaching Point:(.*?)$', scene_content, re.DOTALL | re.IGNORECASE)
            teaching_point = teaching_match.group(1).strip() if teaching_match else "Educational"
            
            current_emotion = emotions[idx % len(emotions)]
            
            character_lower = character_name.lower().replace(" ", "_")
            speaker_id = f"{character_lower}_{voice_tone}"
            
            complete_prompt = f"""===== SCENE {scene_num} (7 SECONDS) =====

VISUAL (VEO 3):
{visual_prompt}

DIALOGUE ({lang_display}):
{dialogue}

TEACHING:
{teaching_point}

=== METADATA ===
Duration: 7-8 seconds (SHORT!)
Style: {visual_style}
Type: {character_type}

VOICE (LOCKED):
Anchor: {voice_anchor}
Audio: {audio_descriptor}
Description: {voice_description}
Emotion: {current_emotion}

SPEAKER:
ID: {speaker_id}
Text: "{dialogue}"
"""

            scenes.append({
                "scene_number": scene_num,
                "visual_prompt": visual_prompt,
                "dialogue": dialogue,
                "emotion": current_emotion,
                "teaching_point": teaching_point,
                "voice_type": voice_description,
                "voice_anchor": voice_anchor,
                "audio_descriptor": audio_descriptor,
                "speaker_id": speaker_id,
                "prompt": complete_prompt,
                "duration": 7,
                "character_type": character_type
            })
            
            print(f"  ✅ Scene {scene_num}: {current_emotion} ({len(dialogue.split())} words)")
        
        print(f"\n✅ Generated {len(scenes)} 7-SECOND scenes")
        print(f"🎤 Anchor: {voice_anchor[:40]}...")
        print(f"🔊 Audio: {audio_descriptor}")
        print(f"{'='*60}\n")
        
        return {
            "scenes": scenes,
            "total_scenes": len(scenes),
            "character_name": character_name,
            "character_type": character_type,
            "voice_locked": voice_description,
            "voice_anchor": voice_anchor,
            "audio_descriptor": audio_descriptor,
            "voice_details": {
                "description": voice_description,
                "anchor": voice_anchor,
                "audio_descriptor": audio_descriptor,
                "pitch": voice_pitch,
                "characteristics": voice_characteristics
            },
            "emotions_used": list(set([s["emotion"] for s in scenes]))
        }


# Global instance
character_dialogue_generator = CharacterDialogueGenerator()