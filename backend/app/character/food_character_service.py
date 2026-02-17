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
        total_duration: int,
        custom_dialogues: str = None  # NEW: User-provided dialogues
    ) -> Dict:
        """Generate food character dialogue with STRICT 8-second pacing"""
        
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
        print(f"📊 Duration: {total_duration}s → Creating {num_scenes} scenes (8s each)")
        
        # Determine visual tone based on topic
        if topic_mode == "side_effects":
            visual_tone = "looking concerned/warning (furrowed brows, serious expression)"
        else:
            visual_tone = "looking happy/friendly (big eyes, friendly smile)"
        
        lang_display = "HINDI (Devanagari + English Terms)" if language == "hindi" else "ENGLISH"
        
        # ✨ NEW: Define global audio signature (like commercial prompt)
        audio_signature = self._get_audio_signature(voice_tone, topic_mode)
        
        # Build scenario context if provided
        scenario_context = ""
        if scenario and scenario.strip():
            scenario_context = f"""
🎬 SCENARIO CONTEXT:
{scenario.strip()}

🚨 CRITICAL: Incorporate this scenario into the VISUAL PROMPTS!
✅ Setting/environment should match the scenario
✅ Character actions/gestures should align with the scenario
✅ Camera angles and lighting should enhance the scenario atmosphere
✅ Keep all {num_scenes} scenes cohesive within this scenario
"""
            print(f"🎬 Using scenario: {scenario[:50]}...")
        
        # Build food-specific prompt - TWO MODES
        if custom_dialogues and custom_dialogues.strip():
            # MODE 1: User provided dialogues - break them into scenes
            print(f"💬 Using custom dialogues ({len(custom_dialogues)} chars)")
            system_prompt = f"""You MUST create EXACTLY {num_scenes} scenes by breaking these dialogues.

USER PROVIDED DIALOGUES:
\"\"\"{custom_dialogues.strip()}\"\"\"
{scenario_context}
🎤 GLOBAL AUDIO SIGNATURE (MAINTAIN ACROSS ALL SCENES):
{audio_signature}

🚨 CRITICAL VOICE CONSISTENCY RULES 🚨:
✅ Scene 1: Include FULL audio signature in Audio Descriptor + "Clear, steady voice at consistent volume level"
✅ Scene 2: "Same voice as Scene 1 - {audio_signature} - maintaining identical volume"
✅ Scene 3+: "CRITICAL: Exact same voice from Scene 1 - {audio_signature} - no volume drop, no tone shift"
✅ ALL scenes must reference the SAME audio signature explicitly
✅ This prevents voice suppression/degradation in later scenes

🚨 CRITICAL REQUIREMENT 🚨:
You MUST generate EXACTLY {num_scenes} scenes. Do NOT generate just 1 scene!
Break the user's dialogues into {num_scenes} equal parts and create one scene for each part.

INSTRUCTIONS:
1. Read ALL the user's dialogues above
2. Divide them into {num_scenes} roughly equal portions
3. Create EXACTLY {num_scenes} scenes (===SCENE 1===, ===SCENE 2===, ===SCENE 3===, etc.)
4. Each scene gets one portion of the dialogues
5. Use the EXACT words from user (no translation, no changes)
6. ADD COMMAS for natural pauses to reach 8-second duration

FORMAT FOR EACH SCENE:
===SCENE X===
Visual Prompt (Veo 3 Format):
Anthropomorphic {character_name}, {visual_style} style. [Detailed appearance - shape, size, color, facial features]. {visual_tone}. [Action/gesture]. [Setting description - kitchen, garden, studio]. [Camera angle]. [Lighting]. No subtitles.

Audio Descriptor:
[Scene 1: "{audio_signature}. Clear, steady voice at consistent volume level."]
[Scene 2: "Same voice as Scene 1 - {audio_signature} - maintaining identical volume and tone."]
[Scene 3+: "CRITICAL: Exact same voice from Scene 1 - {audio_signature} - consistent audio throughout."]

Dialogue ({lang_display}):
[Portion of user's dialogues with COMMAS added for pacing - 25 words for Scene 1, 20 words for other scenes]

Teaching Point:
[What this portion is teaching]
===END SCENE X===

🎤 PACING RULES FOR 8-SECOND DURATION:
✅ Add commas (,) after every 4-6 words to create natural pauses
✅ This ensures the dialogue takes FULL 8 seconds (not 7 seconds)
✅ Commas create ~0.3-0.5 second pauses in speech synthesis
✅ Total: 25 words + 4-5 pauses = exactly 8 seconds
✅ DO NOT rush - comfortable, natural speaking pace

PACING EXAMPLES:
❌ WRONG (7 seconds - too fast):
मैं Apple हूँ और मुझमें Vitamin C है जो आपकी immunity को मजबूत बनाकर शरीर को healthy रखता है।

✅ CORRECT (8 seconds - proper pacing):
मैं Apple हूँ, और मुझमें Vitamin C है, जो आपकी immunity को मजबूत बनाकर, शरीर को healthy रखता है।

🚨 SCENE LIMIT ENFORCEMENT 🚨:
✅ Scene 1: Extract first 25 words from user's dialogues + add commas
✅ Scene 2: Next 20 words from remaining dialogues + add commas
✅ Scene 3: Next 20 words from remaining dialogues + add commas
✅ Continue until ALL {num_scenes} scenes are created
✅ Use ALL of the user's dialogues across all scenes

🎨 VISUAL REQUIREMENTS (80+ words per prompt):
✅ Anthropomorphic {character_name} character
✅ {visual_style} animation style
✅ {visual_tone}
✅ Detailed facial features, expressions, gestures
✅ Rich environment description
✅ Camera work and lighting details

NOW CREATE ALL {num_scenes} SCENES WITH PROPER 8-SECOND PACING:"""
        else:
            # MODE 2: Auto-generate dialogues (original behavior)
            system_prompt = f"""Create {num_scenes} 8-SECOND video scenes about {character_name} ({topic_mode}).

LANGUAGE: {lang_display}
🚨 USE DEVANAGARI FOR HINDI + ENGLISH FOR TERMS
{scenario_context}
🎤 GLOBAL AUDIO SIGNATURE (MAINTAIN ACROSS ALL SCENES):
{audio_signature}

🚨 CRITICAL VOICE CONSISTENCY RULES 🚨:
✅ Scene 1: Include FULL audio signature in Audio Descriptor + "Clear, steady voice at consistent volume level"
✅ Scene 2: "Same voice as Scene 1 - {audio_signature} - maintaining identical volume"
✅ Scene 3+: "CRITICAL: Exact same voice from Scene 1 - {audio_signature} - no volume drop"
✅ Reference the SAME audio signature in EVERY scene's Audio Descriptor
✅ This ensures Veo maintains voice consistency across all scenes

🎭 DIALOGUE TONE & STYLE (MANDATORY - MAKE IT HILARIOUS):
✅ SARCASTIC & WITTY - The food character has ATTITUDE and personality
✅ HILARIOUSLY FUNNY - Make viewers laugh while learning
✅ SELF-AWARE - Food breaking the fourth wall ("Yeah, I'm a talking apple. Deal with it!")
✅ RELATABLE - Use everyday comparisons people understand
✅ PLAYFUL ROASTING - Gently mock bad eating habits or myths
✅ CONVERSATIONAL - Talk like a sassy friend, not a nutrition label
✅ DRAMATIC FLAIR - Treat food facts like movie announcements

❌ AVOID:
❌ Boring, textbook-style facts
❌ Generic "I am healthy" statements
❌ Formal scientific language
❌ Predictable clichés

💡 HUMOR EXAMPLES FOR FOOD CHARACTERS:

🍎 BENEFITS Examples (Funny & Engaging):
"अरे भाई, मैं Apple हूँ! मुझमें Vitamin C है, जो immunity इतनी strong बनाता है, कि cold बोलेगा 'बॉस, माफ़ कीजिए!'"
(Hey bro, I'm an Apple! I have Vitamin C that makes immunity so strong, cold will say 'Boss, sorry!')

"मैं fiber का राजा हूँ! Digestion smooth करूँ, weight control करूँ, और taste में bhi boss! Triple threat जैसा, बिल्कुल!"
(I'm the fiber king! Smooth digestion, weight control, AND tasty! Like a triple threat!)

🥕 SIDE EFFECTS Examples (Sarcastic but Caring):
"हाँ हाँ, मैं Carrot बहुत healthy हूँ, लेकिन overacting mat karo! Zyada खाओगे तो skin orange हो जाएगी। मज़ाक नहीं कर रहा!"
(Yeah yeah, I'm Carrot, very healthy, but don't overact! Eat too much and skin turns orange. Not joking!)

"मुझे excessive mat khao yaar! Otherwise digestion upset ho जाएगा, gas banega, aur sab tumhe blame karenge. Main sirf warning de raha hoon!"
(Don't eat me excessively dude! Otherwise digestion upset, gas happens, and everyone blames you. Just warning!)

🔥 PERSONALITY STYLES:
- CONFIDENT: "मैं जो benefits दूँ, वो कोई और नहीं दे सकता!"
- SASSY: "Workout नहीं करोगे तो मैं भी kya kar लूँगा?"
- HUMOROUS: "मैं Apple हूँ, doctor को भगाता हूँ। Literally! 'An apple a day' वाला!"
- DRAMATIC: "*Epic voice* मुझमें Antioxidants हैं जो body को बीमारी से बचाते हैं!"
- RELATABLE: "3 बजे hunger लगती है ना? That's where I come in, boss!"

For each scene:
===SCENE X===
Visual Prompt (Veo 3 Format):
[Anthropomorphic {character_name}, {visual_style} style]. [Detailed appearance - shape, size, color, facial features]. [{visual_tone}]. [Action/gesture]. [Setting]. [Camera/lighting]. No subtitles.

Audio Descriptor:
[Scene 1: "{audio_signature}. Clear, steady voice at consistent volume level."]
[Scene 2: "Same voice as Scene 1 - {audio_signature} - maintaining identical volume and tone throughout."]
[Scene 3+: "CRITICAL: Exact same voice from Scene 1 - {audio_signature} - consistent audio, no degradation."]

Dialogue ({lang_display}):
[Scene 1: Main {character_name} hoon + ONE fact - 25 WORDS with commas for pacing]
[Scene 2+: ONE fact ONLY - 20 WORDS with commas for pacing]

Teaching Point:
[One fact]
===END SCENE X===

🚨 ABSOLUTE LIMITS (8 SECONDS - NON-NEGOTIABLE) 🚨:
✅ Scene 1: 25 words INCLUDING intro (मैं Apple हूँ। = 4 words, leaves 21 for fact)
✅ Scene 2+: 20 words ONLY - ONE complete sentence
✅ CRITICAL: If using words with 3+ syllables (Antioxidants, Immunity, Magnesium), REDUCE to 18 words MAX
✅ Long words (3+ syllables) count as 1.5 words each for timing
✅ MUST ADD COMMAS every 4-6 words for natural pauses
✅ This ensures FULL 8-second duration (not 7 seconds)
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

🎤 PACING RULES FOR 8-SECOND DURATION:
✅ Add commas (,) after every 4-6 words to create natural pauses
✅ This ensures the dialogue takes FULL 8 seconds (not 7 seconds)
✅ Commas create ~0.3-0.5 second pauses in speech synthesis
✅ Total: 25 words + 4-5 pauses = exactly 8 seconds
✅ DO NOT rush - comfortable, natural speaking pace

🎯 CORRECT EXAMPLES (Devanagari+English - 8 SECOND PACING):
✅ मैं Apple हूँ, और मुझमें Vitamin C है, जो आपकी immunity को मजबूत बनाकर, शरीर को healthy रखता है। (25 words - good)

✅ मैं एक tasty, और healthy fruit हूँ, जो digestion बेहतर करता है, और पूरे दिन natural energy देता है। (20 words - good)

✅ मुझमें भरपूर fiber होता है, जो पेट साफ रखता है, weight control करता है, और आपको fit बनाए रखता है। (20 words - good)

✅ मुझमें Antioxidants होते हैं, जो body को बीमारी से बचाते हैं, और Immunity को boost करते हैं। (18 words - CORRECT for long words)

❌ मुझमें powerful Antioxidants होते हैं, जो body को रोगों से बचाते हैं, और आपकी Immunity को, बहुत boost करते हैं। (28 words - TOO LONG, will cut off!)

🎤 LONG WORD EXAMPLES (3+ syllables - use FEWER total words):
- Antioxidants (5 syllables) = 1.5 words
- Immunity (4 syllables) = 1.5 words  
- Magnesium (4 syllables) = 1.5 words
- Cholesterol (4 syllables) = 1.5 words
- Cardiovascular (5 syllables) = 2 words

RULE: If dialogue has 2+ long words, MAX 18 words total!

🎨 VISUAL RULES:
✅ Anthropomorphic food character (round apple with face, orange carrot)
✅ 3D animation style
✅ {"Concerned/serious/warning facial expressions" if topic_mode == "side_effects" else "Happy/friendly facial expressions (big eyes, friendly smile)"}
✅ Detailed facial features
✅ 80+ words per visual prompt

🎤 AUDIO CONSISTENCY EXAMPLES (CRITICAL FOR VEO):

SCENE 1 Audio Descriptor:
"{audio_signature}. Clear, steady voice at consistent volume level."

SCENE 2 Audio Descriptor:
"Same voice as Scene 1 - {audio_signature} - maintaining identical volume and tone throughout."

SCENE 3 Audio Descriptor:
"CRITICAL: Exact same voice from Scene 1 - {audio_signature} - consistent audio, no degradation."

SCENE 4+ Audio Descriptor:
"Maintain identical voice from Scene 1 - {audio_signature} - clear, steady, consistent throughout."

❌ ABSOLUTE FORBIDDEN ❌:
❌ NO Roman script for Hindi (main, hoon - USE: मैं, हूँ)
❌ NO translating nutrition terms (Vitamin C must stay Vitamin C)
❌ NO dialogue without commas (will speak too fast and finish in 7 seconds)
❌ NO incomplete sentences
❌ NO multiple sentences in one scene
❌ NO "tatha" to add extra words
❌ NO voice anchor in Visual Prompt
❌ NO audio/mic descriptions in Visual Prompt (Audio Descriptor is separate)

CORRECT EXAMPLES:

===SCENE 1===
Visual Prompt:
Anthropomorphic Apple character, rendered in charming 3D animated style. Vibrant red, perfectly round with glossy texture, small brown stem, two bright green leaves. Large expressive cartoon eyes with sparkles, thick eyelashes, wide friendly smile. Standing on white marble kitchen counter, body bouncing enthusiastically. Animated sparkles around suggesting freshness. Bright modern kitchen, soft natural sunlight through window, warm glow. Medium shot at eye level, personable and approachable. Soft lighting highlights glossy surface. No subtitles.

Audio Descriptor:
{audio_signature}. Clear, steady voice at consistent volume level.

Dialogue (HINDI - 8 SECONDS):
मैं Apple हूँ, और मुझमें Vitamin C है, जो आपकी immunity को मजबूत बनाकर, शरीर को healthy रखता है।

Teaching Point:
Apples contain Vitamin C and boost immunity
===END SCENE 1===

===SCENE 2===
Visual Prompt:
Same cheerful red Apple, more confident expression. Eyebrows furrowed helpfully, eyes gleaming. Green leaf extends pointing at glowing red heart icon floating beside, pulsing gently. Soft-focus garden background, lush green grass, bokeh sunlight through leaves, natural healthy atmosphere. Upright proud posture. Close-up on face and heart icon, emphasizing health. Warm golden-hour lighting, optimistic educational feel. No subtitles.

Audio Descriptor:
Same voice as Scene 1 - {audio_signature} - maintaining consistent audio volume as Scene 1.

Dialogue (HINDI - 8 SECONDS):
मैं एक tasty, और healthy fruit हूँ, जो digestion बेहतर करता है, और natural energy देता है।

Teaching Point:
Good for digestion and provides natural energy
===END SCENE 2===

===SCENE 3===
Visual Prompt:
Apple character with satisfied, teaching expression. Eyes wide and engaging, slight head tilt. Both leaves spread out gesturing warmly toward floating vitamin icons glowing softly. Cozy home kitchen setting, wooden cutting board background. Warm afternoon light, golden tones. Medium close-up emphasizing friendly teaching moment. Soft depth of field. No subtitles.

Audio Descriptor:
CRITICAL: Maintain identical voice characteristics and volume from previous scenes - {audio_signature} - clear, steady, consistent audio throughout. Natural, unhurried speech.

Dialogue (HINDI - 8 SECONDS):
मुझमें fiber होता है, जो digestion को improve करता है, और weight को control रखता है।

Teaching Point:
Contains fiber for digestion and weight control
===END SCENE 3===

WRONG EXAMPLES (REJECTED):
❌ "Main Apple hoon. Mujhme Vitamin C hai." (Roman script for Hindi - WRONG)
❌ "मैं सेब हूँ। मुझमें विटामिन सी है।" (Translating Apple, Vitamin - WRONG)
❌ "मैं Apple हूँ और मुझमें Vitamin C है जो immunity बढ़ाता है" (NO COMMAS - too fast, finishes in 7 seconds - WRONG)

Generate {num_scenes} scenes in HINDI (Devanagari + English) with COMMAS for 8-second pacing and VOICE CONSISTENCY:"""
        
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
            scenes = self._parse_scenes(gemini_output, character_name, voice_tone, voice_anchor, visual_style, language, audio_signature)
            
            return {
                "scenes": scenes,
                "total_scenes": len(scenes),
                "character_name": character_name,
                "topic": topic_mode,
                "audio_signature": audio_signature  # ✨ NEW
            }
            
        except Exception as e:
            print(f"❌ Gemini API Error: {str(e)}")
            raise Exception(f"Failed to generate food character dialogue: {str(e)}")
    
    # ✨ NEW: Get audio signature based on voice and topic
    def _get_audio_signature(self, voice_tone: str, topic_mode: str) -> str:
        """Define consistent audio signature for all scenes"""
        
        # Base voice characteristics
        if "child" in voice_tone:
            base_voice = "bright, youthful voice with playful energy"
            pitch = "higher pitch range"
        elif "female" in voice_tone:
            base_voice = "clear, warm female voice"
            pitch = "medium-high pitch"
        else:
            base_voice = "confident, steady male voice"
            pitch = "medium pitch"
        
        # Emotional tone based on topic
        if topic_mode == "side_effects":
            emotion = "concerned, cautionary tone with gentle warning"
            pace = "measured, 95 BPM speaking pace"
        else:
            emotion = "enthusiastic, friendly tone with encouraging inflection"
            pace = "upbeat, 105 BPM speaking pace"
        
        # Combine into signature (like "120 BPM, sub-bass swells")
        return f"{base_voice}, {pitch}, {emotion}, {pace}, natural pauses at commas"
    
    def _parse_scenes(self, gemini_output: str, character_name: str, voice_tone: str, voice_anchor: str, visual_style: str, language: str, audio_signature: str) -> list:
        """Parse Gemini output into structured scenes"""
        scenes = []
        scene_blocks = re.split(r'===SCENE \d+===', gemini_output)[1:]
        
        for i, block in enumerate(scene_blocks, 1):
            if '===END SCENE' not in block:
                continue
            
            block = block.split('===END SCENE')[0].strip()
            
            # Extract sections
            visual_match = re.search(r'Visual Prompt.*?:\s*(.*?)(?=Audio Descriptor|Dialogue|$)', block, re.DOTALL | re.IGNORECASE)
            audio_match = re.search(r'Audio Descriptor.*?:\s*(.*?)(?=Dialogue|$)', block, re.DOTALL | re.IGNORECASE)
            dialogue_match = re.search(r'Dialogue.*?:\s*(.*?)(?=Teaching Point|$)', block, re.DOTALL | re.IGNORECASE)
            teaching_match = re.search(r'Teaching Point.*?:\s*(.*?)(?=$)', block, re.DOTALL | re.IGNORECASE)
            
            visual_prompt = visual_match.group(1).strip() if visual_match else ""
            audio_descriptor = audio_match.group(1).strip() if audio_match else ""
            dialogue = dialogue_match.group(1).strip() if dialogue_match else ""
            teaching_point = teaching_match.group(1).strip() if teaching_match else ""
            
            # Clean up
            visual_prompt = visual_prompt.replace("(HINDI):", "").replace("(HINGLISH):", "").replace("(ENGLISH):", "").replace("(HINDI - 8 SECONDS):", "").replace("(8 SECONDS):", "").strip()
            dialogue = dialogue.replace("(HINDI):", "").replace("(HINGLISH):", "").replace("(ENGLISH):", "").replace("(HINDI - 8 SECONDS):", "").replace("(8 SECONDS):", "").strip()
            
            # Build complete prompt with voice in SPEAKER section only
            complete_prompt = f"""===== SCENE {i} (8 SECONDS) =====

VISUAL (VEO 3):
{visual_prompt}

🎤 AUDIO CONSISTENCY:
Global Signature: {audio_signature}
Scene Audio: {audio_descriptor if audio_descriptor else f"Scene {i} - maintain voice from Scene 1"}

DIALOGUE ({language.upper()} - 8 SEC PACING):
{dialogue}

TEACHING:
{teaching_point}

=== METADATA ===
Duration: 8 seconds (with natural pauses)
Style: {visual_style}
Pacing: Commas indicate 0.3-0.5s pauses
Audio Signature: {audio_signature}

SPEAKER:
ID: {character_name.lower().replace(' ', '_')}_{voice_tone}
Voice: {voice_anchor}
Consistency: {"REFERENCE - establish baseline" if i == 1 else f"MATCH Scene 1 exactly - {audio_signature}"}
Emotion: {"concerned" if "concern" in visual_prompt.lower() else "happy"}
Text: "{dialogue}" """
            
            scenes.append({
                "scene_number": i,
                "dialogue": dialogue,
                "emotion": "concerned" if "concern" in visual_prompt.lower() else "happy",
                "teaching_point": teaching_point,
                "audio_signature": audio_signature,  # ✨ NEW
                "audio_descriptor": audio_descriptor,  # ✨ NEW
                "prompt": complete_prompt
            })
        
        print(f"✅ Parsed {len(scenes)} food character scenes with 8-second pacing and voice consistency")
        return scenes


# Create singleton instance
food_character_generator = FoodCharacterGenerator()