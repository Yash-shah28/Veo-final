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
        """Generate educational character dialogue with distributed character appearances"""
        
        print(f"\n{'='*60}")
        print(f"📚 GENERATING EDUCATIONAL CHARACTER SCENES (DISTRIBUTED MODE)")
        print(f"{'='*60}")
        print(f"Character: {character_name}")
        print(f"Teaching: {scenario}")
        print(f"Language: {language}")
        print(f"Voice Tone: {voice_tone}")
        print(f"Total Duration: {total_duration}s")
        print(f"Custom Voice Description: {custom_voice_description[:80] if custom_voice_description else 'None'}...")
        
        # Extract outfit and teaching topic from scenario
        # This also extracts voice description if it was mixed in the outfit field
        teaching_topic, outfit_description, voice_from_outfit = self._extract_outfit_from_scenario(scenario)
        
        # Calculate 3-POINT scene pattern
        # Character appears for 8 seconds at START, MIDDLE, and END
        # Visual scenes fill the gaps between these anchor points
        num_total_scenes = max(3, total_duration // 8)  # Minimum 3 scenes
        num_character_scenes = 3  # ALWAYS 3: Start, Middle, End (8s each)
        num_visual_scenes = num_total_scenes - num_character_scenes
        
        # Calculate positions for character scenes
        start_position = 1  # First scene
        middle_position = (num_total_scenes // 2) + 1  # Middle scene
        end_position = num_total_scenes  # Last scene
        
        print(f"🎬 Total Scenes: {num_total_scenes} (8 seconds each)")
        print(f"👤 CHARACTER Scenes: {num_character_scenes} x 8s = 24 seconds total")
        print(f"   - Position {start_position}: START (Introduction)")
        print(f"   - Position {middle_position}: MIDDLE (Emphasis)")
        print(f"   - Position {end_position}: END (Conclusion/Pitch)")
        print(f"🎨 VISUAL Scenes: {num_visual_scenes} x 8s = {num_visual_scenes * 8} seconds total")
        print(f"📊 3-Point Pattern: C-V-V-...-C-...-V-V-C")
        
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
        
        lang_display = "HINDI (Devanagari + English Tech Terms)" if language == "hindi" else "ENGLISH"
        
        # Build educational-specific prompt for 3-POINT character structure
        # Character appears for full 8 seconds at START, MIDDLE, and END
        system_prompt = f"""Create {num_total_scenes} scenes (8 seconds each) teaching: {teaching_topic}

🎯 3-POINT STRUCTURE (CRITICAL - EXACT POSITIONS):
- Total scenes: {num_total_scenes} scenes x 8 seconds each
- CHARACTER scenes: 3 scenes (8 seconds each = 24 seconds total)
  * Scene {start_position}: START - Introduction/Hook
  * Scene {middle_position}: MIDDLE - Key Point/Emphasis  
  * Scene {end_position}: END - Conclusion/Call-to-Action
- VISUAL scenes: {num_visual_scenes} scenes (8 seconds each = {num_visual_scenes * 8} seconds total)
  * Fill positions between CHARACTER scenes with teaching illustrations

📋 TEACHING TOPIC: {teaching_topic}
LANGUAGE: {lang_display}

{outfit_instruction}

🎭 DIALOGUE TONE & STYLE (MANDATORY - CRITICAL):
✅ SARCASTIC & WITTY - Use heavy sarcasm, irony, and clever wordplay
✅ HILARIOUSLY FUNNY - Make viewers laugh out loud with unexpected humor
✅ SELF-AWARE - Break the fourth wall, acknowledge you're teaching
✅ RELATABLE - Use everyday analogies that make people go "OMG so true!"
✅ POP CULTURE SAVVY - Reference memes, trends, movies, viral content
✅ PLAYFULLY ROASTING - Gently mock common misconceptions or mistakes
✅ CONVERSATIONAL - Talk like a hilarious friend, not a boring textbook

❌ AVOID:
❌ Generic boring explanations
❌ Formal or overly academic language
❌ Predictable or cliché phrases
❌ Monotonous delivery
❌ Taking yourself too seriously

💡 HUMOR TECHNIQUES TO USE:
1. **Unexpected Comparisons**: "This algorithm is like your ex - it never forgets anything and keeps bringing up old data"
2. **Exaggeration**: "This bug has more relatives than a joint family WhatsApp group"
3. **Self-Deprecating**: "Yeah, I'm explaining this... but let's be real, I still Google it sometimes"
4. **Sarcastic Observations**: "Oh sure, just add more if-else statements. What could possibly go wrong? *Narrator: Everything went wrong*"
5. **Plot Twists**: Start serious, then flip it with humor
6. **Dramatic Flair**: Treat mundane topics like epic movie moments
7. **Relatable Struggles**: "We've all been there at 3 AM debugging this..."
8. **Meta Jokes**: Comment on the teaching process itself

🎯 DIALOGUE EXAMPLES (INSPIRATION):

START Scene Example:
"Alright, buckle up buttercups! Today we're diving into [topic] - and no, you can't Google your way out of this one. Well, you CAN, but where's the fun in that? I'm about to drop knowledge bombs so hard, your brain's gonna need a helmet!"

MIDDLE Scene Example:
"Now here's where it gets spicy! See this? *gestures dramatically* This is what separates the pros from the 'my code works but I don't know why' crowd. And trust me, I've been in that crowd - had a VIP membership and everything!"

END Scene Example:
"And THAT, my friends, is how you [accomplish goal] without losing your sanity! Well, without losing TOO MUCH of it. Side effects may include actually understanding stuff and flexing on your colleagues. You're welcome! 😎"

🔥 MAKE IT MEMORABLE:
- Start with a hook that grabs attention immediately
- Use unexpected metaphors and analogies
- Add dramatic pauses (indicated in dialogue)
- Include rhetorical questions that viewers relate to
- End with a mic-drop moment or satisfying conclusion
- Sprinkle in "real talk" moments of genuine wisdom
- Use humor to explain complex concepts simply

🎬 SCENE TYPES:

TYPE A - CHARACTER SCENE (ON-CAMERA 8 SECONDS):
The educator {character_name} appears ON CAMERA for a FULL 8-second scene
- Duration: 8 seconds (FULL SCENE)
- Dialogue: 25-30 words (complete thought)
- Visual: {character_name} on camera, engaging directly with viewer
- Positions: Scene {start_position} (START), Scene {middle_position} (MIDDLE), Scene {end_position} (END)

TYPE B - CHARACTER SCENE (OFF-SCREEN 8 SECONDS - VISUAL):
Teaching content illustrated while {character_name} continues speaking OFF-SCREEN
- Duration: 8 seconds
- Dialogue: 25-30 words (SAME CALLER MIC VOICE - CONTINUOUS SPEECH)
- Visual: Detailed illustration of teaching point (diagrams, animations, examples)
- Positions: All scenes EXCEPT {start_position}, {middle_position}, and {end_position}
- Purpose: Deep explanation with visual aids while speaker continues talking

🎯 CRITICAL AUDIO RULE:
- ALL scenes use the SAME CALLER MICROPHONE voice
- In Type B scenes, the character is NOT visible, but it is the SAME PERSON speaking
- This is NOT narration. It is CONTINUOUS DIALOGUE from the same speaker.

SCENE FORMAT EXAMPLES:

===SCENE 1 (8 SECONDS – CHARACTER ON-CAMERA)===
SCENE TYPE:
CHARACTER (ON-CAMERA)

VISUAL (VEO 3):
{character_name}, [Style: {visual_style}]. {"[USE EXACT OUTFIT FROM ABOVE]" if outfit_description else "[Professional appearance]"}. [Setting]. Engaging directly with camera. [Action/Gesture]. No subtitles.

DIALOGUE ({lang_display} – CONTINUOUS SPEECH FROM SAME CALLER MIC):
[Intro dialogue text - approx 25 words]

TEACHING:
[Teaching point]
===END SCENE 1===

===SCENE 2 (8 SECONDS – CHARACTER OFF-SCREEN)===
SCENE TYPE:
CHARACTER (OFF-SCREEN CONTINUOUS SPEECH)

VISUAL (VEO 3):
[Detailed illustration description - 150+ words].
NO on-screen character is visible, but the same human speaker from Scene 1 is actively speaking off-screen.
This is NOT narration and NOT AI voice.

DIALOGUE ({lang_display} – CONTINUOUS SPEECH FROM SAME CALLER MIC):
[Explainer dialogue text - approx 25 words]

TEACHING:
[Teaching point]
===END SCENE 2===

=== AUDIO SETTINGS (STRICT – DO NOT OVERRIDE) ===
Input Source: Caller Microphone (Primary)
Voice Capture: Live caller mic only
Audio Mode: Continuous speech from same speaker as Scene 1
No synthetic TTS
No default narration
No voice replacement
No voice enhancement
No pitch, tone, or accent modification

🎙️ VOICE CONTINUITY LOCK:
- Speaker identity is unchanged from Scene 1
- Same human voice continues even when off-screen
- This audio is part of a single continuous explanation
- AI-generated narration is STRICTLY DISABLED

Generate {num_total_scenes} scenes following this exact format:"""
        
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
        """Parse Gemini output into structured scenes with CHARACTER (ON/OFF SCREEN) types"""
        scenes = []
        scene_blocks = re.split(r'===SCENE \d+', gemini_output)[1:]
        
        for i, block in enumerate(scene_blocks, 1):
            if '===END SCENE' not in block:
                continue
            
            block = block.split('===END SCENE')[0].strip()
            
            # Detect scene type
            scene_type = "CHARACTER (OFF-SCREEN)"  # Default
            if "CHARACTER (ON-CAMERA)" in block or "SCENE TYPE:\nCHARACTER (ON-CAMERA)" in block:
                scene_type = "CHARACTER (ON-SCREEN)"
            elif "OFF-SCREEN" in block:
                scene_type = "CHARACTER (OFF-SCREEN)"
            
            # Determine duration (All 8 seconds)
            duration = 8
            
            # Extract sections with updated regex for new headers
            visual_match = re.search(r'VISUAL \(VEO 3\).*?:\s*(.*?)(?=DIALOGUE|$)', block, re.DOTALL | re.IGNORECASE)
            # Match Dialogue with variable header
            dialogue_match = re.search(r'DIALOGUE.*?:\s*(.*?)(?=TEACHING|$)', block, re.DOTALL | re.IGNORECASE)
            teaching_match = re.search(r'TEACHING.*?:\s*(.*?)(?=$)', block, re.DOTALL | re.IGNORECASE)
            
            visual_prompt = visual_match.group(1).strip() if visual_match else ""
            dialogue = dialogue_match.group(1).strip() if dialogue_match else ""
            teaching_point = teaching_match.group(1).strip() if teaching_match else ""
            
            # Clean up headers from dialogue text if caught
            dialogue = re.sub(r'\(.*?\)', '', dialogue).strip()  # Remove parenthetical notes inside dialogue if any
            
            # Build complete prompt with voice description in SPEAKER section only
            complete_prompt = f"""===== SCENE {i} ({duration} SECONDS – {scene_type}) =====

SCENE TYPE:
{scene_type}

VISUAL (VEO 3):
{visual_prompt}

DIALOGUE ({language.upper()} – CONTINUOUS SPEECH FROM SAME CALLER MIC):
{dialogue}

TEACHING:
{teaching_point}

=== METADATA ===
Duration: {duration} seconds
Scene Type: {scene_type}
Style: {visual_style}
Type: educational

=== AUDIO SETTINGS (STRICT – DO NOT OVERRIDE) ===
Input Source: Caller Microphone (Primary)
Voice Capture: Live caller mic only
Audio Mode: Continuous speech from same speaker as Scene 1
No synthetic TTS
No default narration
No voice replacement
No voice enhancement
No pitch, tone, or accent modification

🎙️ VOICE CONTINUITY LOCK:
- Speaker identity is unchanged from Scene 1
- Same human voice continues even when off-screen
- This audio is part of a single continuous explanation
- AI-generated narration is STRICTLY DISABLED

SPEAKER:
ID: {character_name.lower().replace(' ', '_')}_{voice_tone.replace(' ', '_')}
Voice: {master_voice_description}
Source: Same caller microphone as Scene 1
Text: "{dialogue}" """
            
            scenes.append({
                "scene_number": i,
                "scene_type": scene_type,
                "duration": duration,
                "dialogue": dialogue,
                "emotion": "engaging" if "ON-SCREEN" in scene_type else "informative",
                "teaching_point": teaching_point,
                "prompt": complete_prompt,
                "voice_description": master_voice_description
            })
        
        print(f"✅ Parsed {len(scenes)} educational scenes")
        on_screen_scenes = [s for s in scenes if "ON-SCREEN" in s["scene_type"]]
        off_screen_scenes = [s for s in scenes if "OFF-SCREEN" in s["scene_type"]]
        print(f"👤 ON-SCREEN scenes: {len(on_screen_scenes)}")
        print(f"🎨 OFF-SCREEN scenes: {len(off_screen_scenes)}")
        print(f"🎙️ Voice Continuity: ENFORCED (Same Caller Mic)")
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