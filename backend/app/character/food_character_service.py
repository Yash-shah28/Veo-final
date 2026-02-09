# app/character/food_character_service.py
# Food Character Dialogue Generation Service

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict
from app.config import settings
import re

# Voice descriptions are imported from service.py
from app.character.service import VOICE_DESCRIPTIONS


class FoodCharacterGenerator:
    """Generate food character dialogues with benefits/side effects"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            max_output_tokens=8192
        )
    
    async def generate_dialogue(
        self,
        character_name: str,
        voice_tone: str,
        topic_mode: str,  # benefits or side_effects
        scenario: str,
        visual_style: str,
        language: str,
        total_duration: int
    ) -> Dict:
        """Generate food character dialogue with STRICT 7-second limits"""
        
        print(f"\n{'='*60}")
        print(f"🍎 GENERATING FOOD CHARACTER SCENES")
        print(f"{'='*60}")
        print(f"Character: {character_name}")
        print(f"Topic: {topic_mode}")
        print(f"Language: {language}")
        
        # Get voice info
        voice_info = VOICE_DESCRIPTIONS.get(voice_tone)
        if not voice_info:
            print(f"⚠️ Voice '{voice_tone}' not found, falling back")
            voice_info = VOICE_DESCRIPTIONS.get("adult_male", VOICE_DESCRIPTIONS["child_happy"])
            if "female" in voice_tone:
                voice_info = VOICE_DESCRIPTIONS.get("adult_female", voice_info)
        
        voice_anchor = voice_info["anchor_block"]
        
        # Calculate scenes
        num_scenes = max(1, total_duration // 8)
        print(f"📊 Scenes: {num_scenes}")
        
        # Determine visual tone based on topic
        if topic_mode == "side_effects":
            visual_tone = "looking concerned/warning (furrowed brows, serious expression)"
        else:
            visual_tone = "looking happy/friendly (big eyes, friendly smile)"
        
        lang_display = "HINDI (Devanagari + English Terms)" if language == "hindi" else "ENGLISH"
        
        # Build food-specific prompt
        system_prompt = f"""Create {num_scenes} 7-SECOND video scenes about {character_name} ({topic_mode}).

LANGUAGE: {lang_display}
🚨 USE DEVANAGARI FOR HINDI + ENGLISH FOR TERMS

For each scene:
===SCENE X===
Visual Prompt (Veo 3 Format):
[Anthropomorphic {character_name}, {visual_style} style]. [Detailed appearance - shape, size, color, facial features]. [{visual_tone}]. [Action/gesture]. [Setting]. [Camera/lighting]. No subtitles.

Dialogue ({lang_display}):
[Scene 1: Main {character_name} hoon + ONE fact - MAX 20 WORDS]
[Scene 2+: ONE fact ONLY - MAX 15 WORDS]

Teaching Point:
[One fact]
===END SCENE X===

🚨 ABSOLUTE LIMITS (7 SECONDS - NON-NEGOTIABLE) 🚨:
✅ Scene 1: MAX 20 words INCLUDING intro (Main Apple hoon = 3 words, leaves 17 for fact)
✅ Scene 2+: MAX 15 words ONLY - ONE complete sentence
✅ DO NOT include voice anchor or audio descriptor in Visual Prompt
✅ {"Concerned/warning expressions for side effects" if topic_mode == "side_effects" else "Happy/friendly expressions for benefits"}

🗣️ HINDI DIALOGUE RULES (Devanagari + English Terms):
✅ Write Hindi words in DEVANAGARI script (मैं, हूँ, है, को, से, में, मुझमें)
✅ Keep English for terms without good Hindi equivalents:
   - Nutrition: Vitamin, Protein, Calcium, Fiber, Iron, Antioxidant
   - Health: Heart, Immunity, Energy, Digestion, Blood Pressure
   - Food terms: Apple, Carrot, Orange, Banana (keep original names)
   - Modern words: Boost, Healthy, Strong, Fresh
✅ Mix both scripts naturally in same sentence
✅ Sound like casual Indian conversation about food/health

🎯 CORRECT EXAMPLES (Devanagari+English):
✅ "मैं Apple हूँ। मुझमें Vitamin C है।"
✅ "Heart को healthy रखता हूँ।"
✅ "Energy boost करता हूँ।"
✅ "Immunity को strong बनाता हूँ।"

🎨 VISUAL RULES:
✅ Anthropomorphic food character (round apple with face, orange carrot)
✅ 3D Pixar-Disney animation style
✅ {"Concerned/serious/warning facial expressions" if topic_mode == "side_effects" else "Happy/friendly facial expressions (big eyes, friendly smile)"}
✅ Detailed facial features
✅ 80+ words per visual prompt
✅ NO voice anchor or mic descriptions in visual

❌ ABSOLUTE FORBIDDEN ❌:
❌ NO Roman script for Hindi (main, hoon - USE: मैं, हूँ)
❌ NO translating nutrition terms (Vitamin C must stay Vitamin C)
❌ NO dialogue exceeding word limits (will be REJECTED)
❌ NO incomplete sentences
❌ NO multiple sentences in one scene
❌ NO "tatha" to add extra words
❌ NO voice anchor in Visual Prompt
❌ NO audio/mic descriptions in Visual Prompt

CORRECT EXAMPLES:

===SCENE 1===
Visual Prompt:
Anthropomorphic Apple character, rendered in charming 3D Pixar-Disney style. Vibrant red, perfectly round with glossy texture, small brown stem, two bright green leaves. Large expressive cartoon eyes with sparkles, thick eyelashes, wide friendly smile. Standing on white marble kitchen counter, body bouncing enthusiastically. Animated sparkles around suggesting freshness. Bright modern kitchen, soft natural sunlight through window, warm glow. Medium shot at eye level, personable and approachable. Soft lighting highlights glossy surface. No subtitles.

Dialogue (HINDI):
मैं Apple हूँ। मुझमें Vitamin C है।

Teaching Point:
Apples contain Vitamin C
===END SCENE 1===

===SCENE 2===
Visual Prompt:
Same cheerful red Apple, more confident expression. Eyebrows furrowed helpfully, eyes gleaming. Green leaf extends pointing at glowing red heart icon floating beside, pulsing gently. Soft-focus garden background, lush green grass, bokeh sunlight through leaves, natural healthy atmosphere. Upright proud posture. Close-up on face and heart icon, emphasizing health. Warm golden-hour lighting, optimistic educational feel. No subtitles.

Dialogue (HINDI):
Heart को healthy रखता हूँ।

Teaching Point:
Good for heart health
===END SCENE 2===

WRONG EXAMPLES (REJECTED):
❌ "Main Apple hoon. Mujhme Vitamin C hai." (Roman script for Hindi - WRONG)
❌ "मैं सेब हूँ। मुझमें विटामिन सी है।" (Translating Apple, Vitamin - WRONG)


Generate {num_scenes} scenes in HINDI (Devanagari + English) with STRICT limits:"""
        
        # Call Gemini
        try:
            messages = [{"role": "user", "content": system_prompt}]
            # Call Gemini with fallback strategy
            try:
                # Try with primary model (gemini-2.5-flash)
                response = await self.llm.ainvoke(messages)
                gemini_output = response.content
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "resource_exhausted" in error_str:
                    print(f"⚠️ Quota exceeded for gemini-2.5-flash in Food Service. Falling back to gemini-1.5-flash...")
                    # Fallback model
                    fallback_llm = ChatGoogleGenerativeAI(
                        model="gemini-1.5-flash",
                        google_api_key=self.api_key,
                        temperature=0.7,
                        max_output_tokens=8192
                    )
                    try:
                        response = await fallback_llm.ainvoke(messages)
                        gemini_output = response.content
                        print(f"✅ Successfully generated using fallback model gemini-1.5-flash")
                    except Exception as fallback_error:
                        raise Exception(f"Fallback model also failed: {str(fallback_error)}")
                else:
                    raise e
            
            print(f"\n🤖 Gemini Response:\n{gemini_output[:200]}...")
            
            # Parse scenes
            scenes = self._parse_scenes(gemini_output, character_name, voice_tone, voice_anchor, visual_style, language)
            
            return {
                "scenes": scenes,
                "total_scenes": len(scenes),
                "character_name": character_name,
                "topic": topic_mode
            }
            
        except Exception as e:
            print(f"❌ Gemini API Error: {str(e)}")
            raise Exception(f"Failed to generate food character dialogue: {str(e)}")
    
    def _parse_scenes(self, gemini_output: str, character_name: str, voice_tone: str, voice_anchor: str, visual_style: str, language: str) -> list:
        """Parse Gemini output into structured scenes"""
        scenes = []
        scene_blocks = re.split(r'===SCENE \d+===', gemini_output)[1:]
        
        for i, block in enumerate(scene_blocks, 1):
            if '===END SCENE' not in block:
                continue
            
            block = block.split('===END SCENE')[0].strip()
            
            # Extract sections
            visual_match = re.search(r'Visual Prompt.*?:\s*(.*?)(?=Dialogue|$)', block, re.DOTALL | re.IGNORECASE)
            dialogue_match = re.search(r'Dialogue.*?:\s*(.*?)(?=Teaching Point|$)', block, re.DOTALL | re.IGNORECASE)
            teaching_match = re.search(r'Teaching Point.*?:\s*(.*?)(?=$)', block, re.DOTALL | re.IGNORECASE)
            
            visual_prompt = visual_match.group(1).strip() if visual_match else ""
            dialogue = dialogue_match.group(1).strip() if dialogue_match else ""
            teaching_point = teaching_match.group(1).strip() if teaching_match else ""
            
            # Clean up
            visual_prompt = visual_prompt.replace("(HINDI):", "").replace("(HINGLISH):", "").replace("(ENGLISH):", "").strip()
            dialogue = dialogue.replace("(HINDI):", "").replace("(HINGLISH):", "").replace("(ENGLISH):", "").strip()
            
            # Build complete prompt with voice in SPEAKER section only
            complete_prompt = f"""===== SCENE {i} (7 SECONDS) =====

VISUAL (VEO 3):
{visual_prompt}

DIALOGUE ({language.upper()}):
{dialogue}

TEACHING:
{teaching_point}

=== METADATA ===
Duration: 7-8 seconds (SHORT!)
Style: {visual_style}
Type: food

SPEAKER:
ID: {character_name.lower().replace(' ', '_')}_{voice_tone}
Voice: {voice_anchor}
Emotion: {"concerned" if "concern" in visual_prompt.lower() else "happy"}
Text: "{dialogue}" """
            
            scenes.append({
                "scene_number": i,
                "dialogue": dialogue,
                "emotion": "concerned" if "concern" in visual_prompt.lower() else "happy",
                "teaching_point": teaching_point,
                "prompt": complete_prompt
            })
        
        print(f"✅ Parsed {len(scenes)} food character scenes")
        return scenes


# Create singleton instance
food_character_generator = FoodCharacterGenerator()
