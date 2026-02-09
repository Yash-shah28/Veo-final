# app/character/educational_character_service.py
# Educational Character Dialogue Generation Service

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Optional
from app.config import settings
import re

# Voice descriptions are imported from service.py
from app.character.service import VOICE_DESCRIPTIONS


class EducationalCharacterGenerator:
    """Generate educational character dialogues for teaching content"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            max_output_tokens=8192
        )
    
    def _extract_outfit_from_scenario(self, scenario: str) -> tuple[str, str, str]:
        """
        Extract outfit details, teaching topic, and voice description from scenario.
        
        Frontend sends: "Topic. Outfit: outfit details" OR just "Topic"
        The outfit field might contain voice descriptions mixed in.
        
        Returns: (teaching_topic, outfit_description, voice_from_outfit)
        """
        voice_keywords = [
            'voice', 'tone', 'pitch', 'accent', 'speaking', 'sound', 
            'articulation', 'pronunciation', 'timbre', 'resonance',
            'wpm', 'delivery', 'volume', 'vocal', 'audio'
        ]
        
        # Check if scenario has explicit "Outfit:" prefix
        if "Outfit:" in scenario or "outfit:" in scenario:
            parts = scenario.split("Outfit:", 1) if "Outfit:" in scenario else scenario.split("outfit:", 1)
            
            if len(parts) == 2:
                teaching_topic = parts[0].strip().rstrip('.')
                outfit_and_maybe_voice = parts[1].strip()
                
                # Separate outfit from voice in the outfit description
                sentences = outfit_and_maybe_voice.replace('.', '.|').replace(',', ',|').split('|')
                outfit_parts = []
                voice_parts = []
                
                clothing_keywords = [
                    'suit', 'blazer', 'shirt', 'dress', 'jacket', 'tie', 'pants',
                    'jeans', 'coat', 'sweater', 'hoodie', 'vest', 'trousers',
                    'skirt', 'collar', 'sleeve', 'button', 'pocket', 'wearing',
                    'belt', 'printed', 'formal', 'casual', 'glasses', 'watch',
                    'shoes', 'sneakers', 'boots', 'appearence', 'look', 'style'
                ]
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    # CRITICAL: Check for clothing keywords FIRST
                    # If it has clothing, it belongs in outfit, even if it has "calm" or "warm"
                    has_clothing = any(keyword in sentence.lower() for keyword in clothing_keywords)
                    
                    # Check for explicit voice keywords
                    has_voice_keyword = any(keyword in sentence.lower() for keyword in voice_keywords)
                    
                    if has_clothing:
                        outfit_parts.append(sentence)
                        # If it ALSO has voice keywords, we might want to capture them for voice too
                        # but be careful not to trigger on weak words
                        if has_voice_keyword:
                            voice_parts.append(sentence)
                    elif has_voice_keyword:
                        voice_parts.append(sentence)
                    else:
                        # If no keywords matched, but it came from implicit assignment,
                        # assume it's part of the outfit description rather than voice/topic
                        # unless it clearly looks like something else.
                        outfit_parts.append(sentence)
                
                outfit_description = " ".join(outfit_parts).strip()
                voice_from_outfit = " ".join(voice_parts).strip()
                
                print(f"📋 Extracted Topic: {teaching_topic}")
                if outfit_description:
                    print(f"👔 Extracted Outfit: {outfit_description}")
                if voice_from_outfit:
                    print(f"🎙️ Extracted Voice from Outfit: {voice_from_outfit[:80]}...")
                
                return teaching_topic, outfit_description, voice_from_outfit
        
        # Fallback: Check for outfit keywords in scenario
        outfit_keywords = [
            'suit', 'blazer', 'shirt', 'dress', 'jacket', 'tie', 'pants',
            'jeans', 'coat', 'sweater', 'hoodie', 'vest', 'trousers',
            'skirt', 'collar', 'sleeve', 'button', 'pocket', 'tuxedo',
            'uniform', 'robe', 'gown', 'top', 'blouse', 'cardigan', 'wearing'
        ]
        
        scenario_lower = scenario.lower()
        has_outfit = any(keyword in scenario_lower for keyword in outfit_keywords)
        
        if has_outfit:
            sentences = scenario.replace('.', '.|').replace(',', ',|').split('|')
            outfit_parts = []
            topic_parts = []
            voice_parts = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                has_voice_keyword = any(keyword in sentence.lower() for keyword in voice_keywords)
                has_clothing = any(keyword in sentence.lower() for keyword in outfit_keywords)
                
                if has_voice_keyword:
                    voice_parts.append(sentence)
                elif has_clothing:
                    outfit_parts.append(sentence)
                else:
                    topic_parts.append(sentence)
            
            outfit_description = " ".join(outfit_parts).strip().replace('..', '.').strip()
            teaching_topic = " ".join(topic_parts).strip() or scenario
            voice_from_outfit = " ".join(voice_parts).strip()
            
            print(f"📋 Inferred Topic: {teaching_topic}")
            if outfit_description:
                print(f"👔 Inferred Outfit: {outfit_description}")
            if voice_from_outfit:
                print(f"🎙️ Inferred Voice: {voice_from_outfit[:80]}...")
            
            return teaching_topic, outfit_description, voice_from_outfit
        
        # No outfit found - return original scenario as topic
        print(f"📋 Topic: {scenario}")
        print(f"👔 No outfit specified")
        return scenario, "", ""
    
    async def generate_dialogue(
        self,
        character_name: str,
        voice_tone: str,
        custom_voice_description: Optional[str] = None,  # Custom voice from user
        scenario: str = "",  # What to teach
        visual_style: str = "Realistic Character",
        language: str = "hindi",
        total_duration: int = 8
    ) -> Dict:
        """Generate educational character dialogue with STRICT 7-second limits"""
        
        print(f"\n{'='*60}")
        print(f"📚 GENERATING EDUCATIONAL CHARACTER SCENES")
        print(f"{'='*60}")
        print(f"Character: {character_name}")
        print(f"Teaching: {scenario}")
        print(f"Language: {language}")
        print(f"Voice Tone: {voice_tone}")
        print(f"Custom Voice Description: {custom_voice_description[:80] if custom_voice_description else 'None'}...")
        
        # Extract outfit and teaching topic from scenario
        # This also extracts voice description if it was mixed in the outfit field
        teaching_topic, outfit_description, voice_from_outfit = self._extract_outfit_from_scenario(scenario)
        
        # ============================================
        # FIX: Handle custom voice description properly
        # ============================================
        # Check for "I will describe" which is what the frontend sends
        if voice_tone == "I will describe" or voice_tone == "custom":
            print(f"🎙️ CUSTOM VOICE MODE DETECTED")
            
            # Priority: explicit custom_voice_description > voice extracted from outfit field
            if custom_voice_description:
                # Use the custom voice description provided by user
                master_voice_description = self._create_custom_voice_prompt(custom_voice_description)
                print(f"✅ Using Custom Voice (from voice field): {master_voice_description[:100]}...")
            elif voice_from_outfit:
                # User put voice description in outfit field
                master_voice_description = self._create_custom_voice_prompt(voice_from_outfit)
                print(f"✅ Using Custom Voice (from outfit field): {master_voice_description[:100]}...")
            else:
                # Fallback: use friendly male voice
                print(f"⚠️ Custom voice selected but no description provided, using default")
                voice_info = VOICE_DESCRIPTIONS.get("male_friendly", VOICE_DESCRIPTIONS["adult_male"])
                master_voice_description = voice_info.get("master_voice_prompt", voice_info["anchor_block"])
        else:
            # Use predefined voice from VOICE_DESCRIPTIONS
            voice_info = VOICE_DESCRIPTIONS.get(voice_tone)
            if not voice_info:
                print(f"⚠️ Voice '{voice_tone}' not found, falling back")
                # Smart fallback based on voice_tone name
                if "female" in voice_tone.lower():
                    voice_info = VOICE_DESCRIPTIONS.get("female_friendly", VOICE_DESCRIPTIONS["adult_female"])
                elif "male" in voice_tone.lower():
                    voice_info = VOICE_DESCRIPTIONS.get("male_friendly", VOICE_DESCRIPTIONS["adult_male"])
                elif "child" in voice_tone.lower():
                    voice_info = VOICE_DESCRIPTIONS.get("child_happy", VOICE_DESCRIPTIONS["adult_male"])
                else:
                    voice_info = VOICE_DESCRIPTIONS["adult_male"]
            
            # USE MASTER VOICE PROMPT - This is the detailed, technical description
            master_voice_description = voice_info.get("master_voice_prompt", voice_info["anchor_block"])
            print(f"✅ Using Predefined Voice: {master_voice_description[:100]}...")
        
        if outfit_description:
            outfit_instruction = f"""
🎨 OUTFIT RULE (MANDATORY - CRITICAL):
The scenario specifies this outfit:
"{outfit_description}"

✅ USE THIS EXACT OUTFIT IN EVERY SINGLE SCENE
✅ Copy this outfit description word-for-word in all Visual Prompts
✅ DO NOT modify, add to, or change this outfit
✅ DO NOT invent additional clothing items
✅ Maintain EXACT same outfit across all {total_duration // 8} scenes

Example Visual Prompt Start:
{character_name}, [Style: {visual_style}]. {outfit_description}. [Rest of description...]
"""
        else:
            outfit_instruction = f"""
🎨 OUTFIT RULE (NO OUTFIT SPECIFIED):
❌ DO NOT invent or describe any clothing details
❌ DO NOT mention: suit, shirt, pants, dress, jacket, etc.
✅ ONLY describe: character style, facial expression, body language, setting, lighting
✅ Start Visual Prompt with: "{character_name}, [Style: {visual_style}], professional appearance."
✅ Then focus on: emotion, gesture, background, camera angle

Example Visual Prompt Start:
{character_name}, [Style: {visual_style}], professional appearance. Standing confidently in [setting]. [Expression and gesture]. [Camera and lighting]. No subtitles.
"""
        
        # Calculate scenes
        num_scenes = max(1, total_duration // 8)
        print(f"🎬 Scenes: {num_scenes}")
        
        lang_display = "HINDI (Devanagari + English Tech Terms)" if language == "hindi" else "ENGLISH"
        
        # Build educational-specific prompt using clean teaching topic
        system_prompt = f"""Create {num_scenes} 7-SECOND scenes where {character_name} explains: {teaching_topic}

LANGUAGE: {lang_display}
🚨 USE NATURAL HINGLISH (Roman Script)

📋 TEACHING TOPIC: {teaching_topic}

{outfit_instruction}

For each scene:
===SCENE X===
Visual Prompt (Veo 3 Format):
{character_name}, [Style: {visual_style}]. {"[USE EXACT OUTFIT FROM ABOVE]" if outfit_description else "[Professional appearance - NO clothing details]"}. [Setting]. [Action/Emotion]. [Camera/lighting]. No subtitles.

Dialogue ({lang_display}):
[Scene 1: Main {character_name} hoon + ONE point - MAX 25 WORDS]
[Scene 2+: ONE fact ONLY - MAX 20 WORDS]

Teaching Point:
[Key point]
===END SCENE X===

🚨 ABSOLUTE LIMITS (7 SECONDS - NON-NEGOTIABLE) 🚨:
✅ Scene 1: MAX 25 words (intro + one point)
✅ Scene 2+: MAX 20 words - ONE complete thought
✅ DO NOT include voice anchor or audio descriptor in Visual Prompt
✅ {"Use EXACT outfit specified above" if outfit_description else "NO clothing descriptions allowed"}

🗣️ HINDI DIALOGUE RULES (Devanagari + English Tech Terms):
✅ Write Hindi words in DEVANAGARI script (आज, मैं, आपको, बताऊँगा, कैसे, etc.)
✅ Keep technical/modern terms in ENGLISH (Latin script):
   - Technical: AI, ML, API, Cloud, Server, Database, Algorithm, Code, Query
   - Modern: Video, Audio, Digital, Online, App, Software, Hardware
   - Business: Meeting, Presentation, Project, Schedule, Deadline
   - Numbers: 50%, 100MB, 5 minutes | Brands: Google, Python, AWS
✅ Mix both scripts naturally in same sentence
✅ Sound like Indian teacher speaking proper Hindi with English tech terms

🎯 CORRECT EXAMPLES (Devanagari+English):
✅ "आज मैं आपको बताऊँगा कि AI वीडियो कैसे बनाए जाते हैं।"
✅ "Database में data सेव करने के लिए query लिखनी पड़ती है।"
✅ "सबसे पहले server की availability चेक करनी चाहिए।"
✅ "यह algorithm बहुत तेज़ है और अच्छा performance देता है।"

🎨 VISUAL RULES:
✅ Realistic Character style
✅ {"EXACT outfit from scenario: " + outfit_description if outfit_description else "NO clothing descriptions - focus on expression/setting only"}
✅ Detailed setting (digital studio, tech lounge, whiteboard)
✅ 100+ words per visual prompt
✅ NO voice anchor or mic descriptions in visual

❌ ABSOLUTE FORBIDDEN ❌:
❌ NO Roman script for Hindi words (aaj, main - USE: आज, मैं)
❌ NO translating technical terms (AI must stay AI, not कृत्रिम बुद्धिमत्ता)
❌ NO dialogue exceeding limits (WILL BE REJECTED)
❌ NO incomplete sentences
❌ NO multiple sentences per scene
❌ NO voice anchor in Visual Prompt
❌ NO audio/mic descriptions in Visual Prompt
❌ {"NO inventing outfits when none specified" if not outfit_description else "NO modifying the specified outfit"}

CORRECT EXAMPLES (7 SECONDS):

===SCENE 1===
Visual Prompt:
{"Yagnesh Modh, Realistic Character style, brightly lit modern digital studio. Smart green suit over crisp white collared shirt." if outfit_description else "Yagnesh Modh, Realistic Character style, professional appearance, brightly lit modern digital studio."} Genuine engagement, eyebrows raised, warm inviting smile. Leaning forward, direct eye contact with camera, personally addressing viewer. Hands open, palms upward, welcoming gesture drawing audience in. Background: subtle dynamic abstract digital patterns, cool blues and greens, technological innovation hints, not distracting. Eye-level medium shot, expressive upper body, inviting posture. Soft even studio lighting highlights features, approachable knowledgeable demeanor. No subtitles.

Dialogue (HINDI):
आज मैं आपको बताऊँगा कि AI वीडियो कैसे बनाए जाते हैं।

Teaching Point:
Introduction to AI video generation
===END SCENE 1===

===SCENE 2===
Visual Prompt:
{"Yagnesh Modh beside transparent digital whiteboard. Green suit, white shirt crisp." if outfit_description else "Yagnesh Modh beside transparent digital whiteboard, professional appearance."} Focused explanatory expression, slight brow furrow showing concentration. Right hand holds sleek futuristic stylus, pointing precisely at animated diagram on board. Diagram shows glowing nodes, flowing connections representing regeneration. Head tilted explaining, gaze shifting between diagram and camera. Bright focused lighting from board illuminates face, emphasizing content. Medium-wide shot frames Yagnesh and whiteboard, visual aid emphasis. No subtitles.

Dialogue (HINDI):
हर regeneration में characters बदल जाते हैं।

Teaching Point:
AI characters vary each generation
===END SCENE 2===

WRONG EXAMPLES (REJECTED):
❌ "Aaj main aapko bataunga AI videos kaise banate hain" (Roman script for Hindi - WRONG)
❌ "आज मैं आपको बताऊँगा कि कृत्रिम बुद्धिमत्ता वीडियो..." (Translating AI - WRONG)
❌ {"Inventing blazer when not specified" if not outfit_description else "Changing green suit to blue blazer"}

Generate {num_scenes} scenes in HINDI (Devanagari + English) with STRICT limits:"""
        
        # Call Gemini
        try:
            messages = [{"role": "user", "content": system_prompt}]
            response = await self.llm.ainvoke(messages)
            gemini_output = response.content
            
            print(f"\n🤖 Gemini Response:\n{gemini_output[:200]}...")
            
            # Parse scenes - pass master_voice_description instead of anchor_block
            scenes = self._parse_scenes(
                gemini_output, 
                character_name, 
                voice_tone, 
                master_voice_description,
                visual_style, 
                language
            )
            
            return {
                "scenes": scenes,
                "total_scenes": len(scenes),
                "character_name": character_name,
                "topic": "educational"
            }
            
        except Exception as e:
            print(f"❌ Gemini API Error: {str(e)}")
            raise Exception(f"Failed to generate educational character dialogue: {str(e)}")
    
    def _parse_scenes(
        self, 
        gemini_output: str, 
        character_name: str, 
        voice_tone: str, 
        master_voice_description: str,
        visual_style: str, 
        language: str
    ) -> list:
        """Parse Gemini output into structured scenes with STATIC master voice prompt"""
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
            visual_prompt = visual_prompt.replace("(HINGLISH):", "").replace("(ENGLISH):", "").strip()
            dialogue = dialogue.replace("(HINGLISH):", "").replace("(ENGLISH):", "").strip()
            
            # Build complete prompt with voice description in SPEAKER section only
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
Type: educational

SPEAKER:
ID: {character_name.lower().replace(' ', '_')}_{voice_tone.replace(' ', '_')}
Voice: {master_voice_description}
Text: "{dialogue}" """
            
            scenes.append({
                "scene_number": i,
                "dialogue": dialogue,
                "emotion": "engaging",
                "teaching_point": teaching_point,
                "prompt": complete_prompt,
                "voice_description": master_voice_description  # Store for reference
            })
        
        print(f"✅ Parsed {len(scenes)} educational character scenes")
        print(f"🎙️ All scenes use STATIC voice: {master_voice_description[:80]}...")
        return scenes
    
    def _create_custom_voice_prompt(self, custom_description: str) -> str:
        """
        Convert user's custom voice description into a structured voice prompt
        
        This method creates a clean, direct voice prompt similar to predefined voices
        """
        # Clean up the description
        custom_description = custom_description.strip()
        
        # Create a simple, direct prompt similar to predefined voice prompts
        # This format works better with TTS systems
        custom_prompt = f"{custom_description}. Clean audio, professional recording quality."
        
        return custom_prompt

    
    def _extract_voice_description(self, description: str) -> str:
        """Extract voice characteristics from user description"""
        
        # Voice-related keywords to look for
        voice_keywords = ["voice", "tone", "pitch", "accent", "speaking", "sound", "talk", "articulation"]
        
        # Find sentences containing voice keywords
        sentences = description.replace('.', '.\n').replace(',', ',\n').split('\n')
        voice_parts = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in voice_keywords):
                voice_parts.append(sentence)
        
        # If voice description found, combine them
        if voice_parts:
            voice_description = " ".join(voice_parts).strip()
        else:
            # Fallback: create basic voice description from description hints
            desc_lower = description.lower()
            
            # Detect gender
            if "female" in desc_lower or "woman" in desc_lower:
                voice_description = "Clear female voice, moderate pitch, neutral accent, professional tone"
            elif "male" in desc_lower or "man" in desc_lower:
                voice_description = "Clear male voice, moderate pitch, neutral accent, professional tone"
            else:
                voice_description = "Clear professional voice, moderate pitch, neutral accent, authoritative tone"
        
        return voice_description


# Create singleton instance
educational_character_generator = EducationalCharacterGenerator()