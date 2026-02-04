from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from app.config import settings
import re

class CharacterDialogueGenerator:
    """Service for generating talking character dialogues using Gemini"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        # Initialize Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=self.api_key,
            temperature=1.0,  # Maximum creativity
            max_output_tokens=8192
        )
        
        # Simple prompt template for plain text generation
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Veo AI video prompt engineer creating DETAILED, CINEMATIC educational videos.

CRITICAL: Generate 200-300 WORD visual descriptions with microscopic/cinematic detail!

FORMAT for each scene:

===SCENE X===

Visual Prompt:
[WRITE 200-300 WORDS! Describe environment, character appearance, movements, camera angles, lighting, colors, mood, visual effects. BE EXTREMELY DETAILED AND CINEMATIC! Each scene should show DIFFERENT location/action inside body or environment.]

Dialogue:
[30-40 words - MUST mention SPECIFIC health effects like blood sugar, heart problems, cholesterol, laziness, immunity, energy, etc. Make it educational with real health impacts!]

===END SCENE X===

DIALOGUE RULES:
- 30-40 words per dialogue (enough for 8 seconds)
- Mention SPECIFIC health effects:
  * Side Effects: blood sugar spikes, heart disease, clogged arteries, obesity, laziness, liver damage, cholesterol, diabetes
  * Benefits: vitamins, immunity boost, strong bones, sharp mind, heart health, energy, longevity
- Each scene progresses the story with NEW information
- Make it dramatic and educational!

VISUAL DESCRIPTION RULES:

For SIDE EFFECTS topics:
- Dark, ominous, microscopic environments (inside body, veins, organs)
- Scene 1: Blood vessels/arteries clogging
- Scene 2: Heart under stress
- Scene 3: Cells/metabolism slowing (laziness)
- Scene 4: Organ damage (liver, pancreas)
- Menacing character with angry/serious expression
- Dark colors: blacks, deep reds, purples, sickly yellows
- Threatening movements and gestures
- Visual metaphors: cholesterol buildup, blood thickening, organs failing
- Camera: close-ups, dramatic angles
- Lighting: dim, pulsating, ominous glows
- Mood: serious warning, threatening

For BENEFITS topics:
- Bright, cheerful environments (both natural and inside healthy body)
- Scene 1: Nutrient-rich environment
- Scene 2: Immune system strengthening
- Scene 3: Bones/brain getting stronger
- Scene 4: Heart health & longevity
- Happy character with friendly smile
- Vibrant colors: greens, yellows, oranges, blues, whites
- Energetic, welcoming gestures
- Visual metaphors: vitamins floating, white blood cells strong, energy flowing
- Camera: wide shots, inviting angles
- Lighting: bright, warm, sunny
- Mood: positive, educational, encouraging

EXAMPLE 1 - Sugar Side Effects (Scene 1):

Visual Prompt:
The scene opens inside a human blood vessel, showing a cross-section view of an artery. The vein walls appear slightly rough and discolored, showing early signs of damage. The Sugar character—a larger, menacing animated sugar crystal—floats in the center of the bloodstream with an angry, threatening expression. Its crystalline form shimmers with dark energy, edges sharp and threatening. Around it, cholesterol plaques are forming on the artery walls, shown as yellow-white fatty deposits that narrow the passage. Red blood cells struggle to squeeze through the restricted space. As the Sugar character speaks, it gestures aggressively, and with each gesture, more fatty deposits accumulate on the walls. The blood flow visibly slows and thickens, becoming sluggish and viscous. The lighting is dim and ominous with a faint reddish glow. Dark colors dominate—blacks, deep reds, purples. The camera does a slow push-in toward the narrowing artery, creating a claustrophobic, threatening feeling. Visual effects show pulsating glows from the character and the accumulating plaque. The overall mood is ominous and educational, showing the real harm sugar causes to cardiovascular health.

Dialogue (Hindi):
चेतावनी! ज़्यादा मिठास खाने से ब्लड शुगर तेज़ी से बढ़ता है, मोटापा होता है, हृदय रोग आते हैं और धमनियों में रुकावट हो जाती है!

EXAMPLE 2 - Apple Benefits (Scene 1):

Visual Prompt:
The scene opens in a vibrant environment representing nutrition and health. The Apple character stands center frame with a huge, welcoming smile and sparkling, expressive eyes. It's surrounded by animated, glowing symbols of nutrition—large vitamin C letters shimmer with golden light, vitamin A symbols float as orange sparkles, minerals sparkle like small stars, and antioxidants appear as protective shields. The character gestures enthusiastically outward toward the viewer, its arms moving with infectious energy. The background is a beautiful gradient of warm, inviting colors—oranges fading to yellows fading to soft greens. Golden sunlight streams from above in visible rays, creating a magical, wholesome atmosphere. Small particles of light dance in the air. The camera does a gentle 360-degree orbit around the character, showing the vitamins from all angles. Everything in the scene pulses with life and vitality. The mood is cheerful, empowering, and positive, designed to make viewers excited about healthy eating.

Dialogue (Hindi):
नमस्ते! मैं सेब हूँ! मुझमें विटामिन सी भरपूर है जो रोग प्रतिरोधक क्षमता बढ़ाता है, आपको ताकतवर बनाता है और हर दिन स्वस्थ रखता है!

REMEMBER:
- 200-300 words per visual description!
- 30-40 words per dialogue with SPECIFIC health effects!
- Each scene DIFFERENT - different body part or environment!
- Adapt to topic (dark for side effects, bright for benefits)
- Use cinematic language
- Describe everything: environment, character, movement, lighting, mood
- Progress the educational story across scenes!"""),
            ("user", """Generate {num_scenes} UNIQUE scenes for:

CHARACTER: {character_name}
TOPIC: {topic_mode}
SCENARIO: {topic_desc}
VISUAL STYLE: {visual_style}
LANGUAGE: {language}
DURATION: {total_duration} seconds = {num_scenes} scenes

IMPORTANT:
- Generate DETAILED 200-300 word visual descriptions
- If topic is about side effects: use dark, ominous, microscopic settings
- If topic is about benefits: use bright, cheerful, natural settings
- Each scene must have DIFFERENT dialogue
- Make it educational and cinematic!

Output {num_scenes} scenes with ===SCENE X=== markers.""")
        ])
    
    async def generate_character_dialogue(
        self,
        character_name: str,
        voice_tone: str,
        topic_mode: str,
        scenario: str,
        visual_style: str,
        language: str,
        total_duration: int
    ) -> dict:
        """Generate character dialogue broken into 8-second scenes"""
        try:
            # Calculate scenes
            num_scenes = max(1, total_duration // 8)
            
            # Prepare variables
            character_lower = character_name.lower()
            lang_display = "HINDI (Devanagari)" if language == "hindi" else "ENGLISH"
            full_language = "Hindi" if language == "hindi" else "English"
            
            # Voice mapping
            voice_map = {
                "male_strong": ("Deep, resonant, strong MALE voice", "angry"),
                "male_friendly": ("Warm, friendly MALE voice", "cheerful"),
                "female_soft": ("Gentle, soothing FEMALE voice", "calm"),
                "female_friendly": ("Friendly, warm FEMALE voice", "happy"),
                "child_happy": ("Cute, playful child voice", "excited"),
                "child_excited": ("Energetic, enthusiastic child voice", "very excited"),
                "cheerful": ("Upbeat, energetic voice", "joyful"),
                "calm": ("Soothing, peaceful voice", "serene"),
                "wise": ("Knowledgeable teacher voice", "confident"),
                "cartoon": (" Silly, animated voice", "playful"),
                "superhero": ("Brave, heroic voice", "confident"),
                "narrator": ("Clear storytelling voice", "neutral")
            }
            
            voice_desc, emotion_val = voice_map.get(voice_tone, ("Friendly voice", "neutral"))
            
            # Topic description
            if topic_mode == "benefits":
                topic_desc = f"health benefits of eating {character_name}, why it's good for you"
            else:
                topic_desc = f"side effects and health problems from eating too much {character_name}. {scenario}"
            
            # Format prompt
            formatted_prompt = self.prompt.format_messages(
                character_name=character_name,
                voice_tone=voice_tone,
                topic_mode=topic_mode,
                topic_desc=topic_desc,
                visual_style=visual_style,
                language=full_language,
                total_duration=total_duration,
                num_scenes=num_scenes
            )
            
            # Get AI response
            print(f"\n{'='*60}\n🤖 CALLING GEMINI with {num_scenes} scenes\n{'='*60}")
            response = await self.llm.ainvoke(formatted_prompt)
            content = response.content
            
            print(f"🤖 Gemini Response Length: {len(content)} characters")
            print(f"📝 First 500 chars:\n{content[:500]}\n{'='*60}\n")
            
            # Parse scenes manually
            scenes = []
            scene_blocks = re.split(r'===SCENE \d+===', content)
            
            print(f"🔍 Found {len(scene_blocks)} blocks (first is empty)")
            
            for i, block in enumerate(scene_blocks[1:], 1):  # Skip first empty element
                if not block.strip():
                    continue
                    
                scene_num = i
                
                # Extract sections
                visual_match = re.search(r'Visual Prompt:\s*\n(.*?)\n\nDialogue', block, re.DOTALL)
                dialogue_match = re.search(r'Dialogue[^:]*:\s*\n(.*?)\n\n', block, re.DOTALL)
                
                visual_prompt = visual_match.group(1).strip() if visual_match else f"Scene with {character_name} character explaining {topic_mode}"
                dialogue = dialogue_match.group(1).strip() if dialogue_match else f"Scene {scene_num} dialogue"
                
                print(f"Scene {scene_num} - Dialogue: {dialogue[:50]}...")
                
                # Create complete formatted prompt
                complete_prompt = f"""Visual Prompt:
{visual_prompt}

Dialogue ({lang_display}):
{dialogue}

[SCENE METADATA]
Duration: 8 seconds
Aspect Ratio: 9:16

[AUDIO STYLE]
Voice: {voice_desc}. Pitch/Timbre: {voice_tone}. Emotion: {emotion_val}.
Background: {'Low ominous hum' if topic_mode == 'side_effects' else 'Upbeat background music'}

[LIP SYNC DATA]
0.0s-8.0s
Speaker: {character_lower}
Voice ID: {character_lower}_{voice_tone}
Lip Sync Target: {character_lower}_face_mesh
Text: "{dialogue}"
"""
                
                scenes.append({
                    "scene_number": scene_num,
                    "visual_prompt": visual_prompt,
                    "dialogue": dialogue,
                    "emotion": emotion_val,
                    "teaching_point": f"{topic_mode.title()} - Scene {scene_num}",
                    "voice_type": voice_desc,
                    "voice_emotion": emotion_val,
                    "background_audio": "Low ominous hum" if topic_mode == "side_effects" else "Upbeat background music",
                    "speaker_id": f"{character_lower}_{voice_tone}",
                    "prompt": complete_prompt
                })
            
            # If parsing failed, use fallback
            if not scenes or len(scenes) < num_scenes:
                print(f"⚠️ Only parsed {len(scenes)} scenes, expected {num_scenes}. Using fallback.")
                return self._fallback_dialogue(character_name, topic_mode, language, total_duration, voice_tone)
            
            print(f"✅ Successfully generated {len(scenes)} unique scenes!\n")
            
            return {
                "scenes": scenes,
                "total_scenes": len(scenes),
                "character_name": character_name,
                "topic": f"{character_name} - {topic_mode}"
            }
            
        except Exception as e:
            import traceback
            print(f"❌ Error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return self._fallback_dialogue(character_name, topic_mode, language, total_duration, voice_tone)
    
    def _fallback_dialogue(self, character_name: str, topic_mode: str, language: str, total_duration: int, voice_tone: str = "child_happy") -> dict:
        """Fallback dialogue generation if AI fails - NOW WITH UNIQUE DIALOGUES"""
        num_scenes = max(1, total_duration // 8)
        
        character_lower = character_name.lower()
        speaker_id = f"{character_lower}_{voice_tone}"
        lang_display = "HINDI (Devanagari)" if language == "hindi" else "ENGLISH"
        
        # Generate DIFFERENT dialogues for each scene
        if topic_mode == "benefits":
            if language == "hindi":
                dialogues = [
                    f"नमस्ते! मैं {character_name} हूँ! मुझमें पोषण भरपूर है!",
                    f"मैं तुम्हें ताकतवर बनाऊंगा, स्वस्थ रखूंगा!",
                    f"रोज मुझे खाओ, बीमारियों से बचो!",
                    f"विटामिन और एनर्जी दूंगा मैं तुम्हें!",
                    f"मुझे खाकर तुम हमेशा  खुश रहोगे!"
                ]
            else:
                dialogues = [
                    f"Hi! I'm {character_name}! I'm super nutritious!",
                    f"I'll make you strong and healthy!",
                    f"Eat me daily to fight diseases!",
                    f"I'm packed with vitamins and energy!",
                    f"Eating me will keep you happy!"
                ]
        else:  # side_effects
            if language == "hindi":
                dialogues = [
                    f"चेतावनी! ज़्यादा {character_name} खाना खतरनाक है!",
                    f"मैं तुम्हारी सेहत बिगाड़ सकता हूँ!",
                    f"मोटापा, बीमारी - सब मैं लाऊंगा!",
                    f"तुम्हारे शरीर को नुकसान पहुंचाऊंगा!",
                    f"सावधान रहो, मुझसे बचो!"
                ]
            else:
                dialogues = [
                    f"Warning! Too much {character_name} is dangerous!",
                    f"I can harm your health badly!",
                    f"I bring obesity and disease!",
                    f"I'll damage your body systems!",
                    f"Be careful, avoid too much of me!"
                ]
        
        scenes = []
        
        # Define specific health effects for common foods
        health_effects_map = {
            "benefits": {
                "dialogues_hindi": [
                    f"नमस्ते! मैं {character_name} हूँ! मुझमें भरपूर पोषण है जो आपको ताकतवर बनाता है, ऊर्जा देता है और आपको स्वस्थ रखता है!",
                    f"मैं आपकी रोग प्रतिरोधक क्षमता बढ़ाता हूँ! विटामिन और मिनरल्स से भरपूर हूँ जो बीमारियों से लड़ने में मदद करते हैं!",
                    f"रोज मुझे खाने से आपकी हड्डियाँ मजबूत होती हैं, दिमाग तेज़ होता है और शरीर में नई ऊर्जा आती है!",
                    f"मैं आपके दिल को स्वस्थ रखता हूँ, पाचन तंत्र को सुधारता हूँ और आपको लंबी उम्र तक फिट रखता हूँ!"
                ],
                "dialogues_english": [
                    f"Hello! I'm {character_name}! I'm packed with nutrition that makes you stronger, gives you energy and keeps you healthy every day!",
                    f"I boost your immune system! Full of vitamins and minerals that help your body fight diseases and stay strong!",
                    f"Eating me daily strengthens your bones, sharpens your mind and fills your body with fresh energy and vitality!",
                    f"I keep your heart healthy, improve your digestion and help you stay fit for a long, active life!"
                ]
            },
            "side_effects": {
                "dialogues_hindi": [
                    f"चेतावनी! ज़्यादा {character_name} खाने से ब्लड शुगर तेज़ी से बढ़ता है, मोटापा होता है और दिल की बीमारियाँ हो सकती हैं!",
                    f"मैं आपकी धमनियों में रुकावट पैदा करता हूँ! खून गाढ़ा होता है, दिल पर दबाव बढ़ता है और हार्ट अटैक का खतरा बढ़ जाता है!",
                    f"ज़्यादा सेवन से आप सुस्त हो जाते हैं! आलस बढ़ता है, थकान रहती है और शरीर में सूजन आ जाती है!",
                    f"मैं आपके लीवर को नुकसान पहुंचाता हूँ, कोलेस्ट्रॉल बढ़ाता हूँ और डायबिटीज जैसी गंभीर बीमारियाँ लाता हूँ!"
                ],
                "dialogues_english": [
                    f"Warning! Too much {character_name} spikes your blood sugar rapidly, causes obesity and can lead to serious heart diseases!",
                    f"I clog your arteries! Blood thickens, pressure on heart increases and risk of heart attack goes way up dangerously!",
                    f"Excess consumption makes you lazy and sluggish! Fatigue increases, inflammation spreads and your body weakens significantly!",
                    f"I damage your liver, raise cholesterol levels high and bring serious diseases like diabetes and hypertension!"
                ]
            }
        }
        
        # Get appropriate dialogues
        dialogues = health_effects_map[topic_mode][f"dialogues_{language}"]
        
        # Scene-specific visual environments for side effects
        side_effects_visuals = [
            # Scene 1: Blood vessels / cardiovascular
            f"The scene opens inside a human blood vessel, showing a cross-section view of an artery. The {character_name} character, large and menacing, floats in the bloodstream with an angry, threatening expression. Around it, cholesterol plaques are forming on the artery walls, shown as yellow-white deposits narrowing the passage. Red blood cells struggle to flow through the restricted space. The {character_name} character gestures aggressively, and as it does, more fatty deposits accumulate, making the blood flow slower and thicker. The lighting is dim with a sickly yellow-red glow. Dark reds and purples dominate. The camera does a slow push-in, emphasizing the dangerous narrowing. The mood is ominous and educational.",
            
            # Scene 2: Heart under stress
            f"The scene shifts to show a human heart beating, but struggling visibly. The {character_name} character appears standing on top of the heart muscle, which is pulsating irregularly. With each heartbeat, the character presses down with force, representing the increased cardiac workload. The heart muscle appears strained, with darker patches indicating stress. Electrical signals (shown as erratic lightning-like pulses) flash irregularly. The {character_name} character's expression is severe and commanding. The color palette shifts to deeper reds and blacks. Harsh, pulsating lighting creates a sense of danger. The camera angle is a dramatic low angle looking up at the character dominating the weakening heart.",
            
            # Scene 3: Body sluggishness / metabolism
            f"The scene transitions to a view inside a human cell, showing mitochondria (the energy factories) slowing down and dimming. The {character_name} character sits lazily in the center, surrounded by sluggish, slow-moving particles. Energy molecules (ATP) are depicted as fading, dim lights instead of bright ones. The cell membrane looks less vibrant. The character yawns or gestures tiredly, representing the lethargy it causes. The color palette is dull - muddy browns, grays, and faded colors. The lighting is low and lifeless. Everything moves in slow motion. The camera slowly zooms out, showing more and more cells affected by this sluggishness.",
            
            # Scene 4: Liver damage / organ stress
            f"The final scene shows a human liver, with the {character_name} character looming over liver cells that appear damaged and inflamed. Some cells are visibly swollen or darkened, indicating fatty liver disease. The character points accusingly at the damaged areas, which glow with an unhealthy greenish-yellow hue. Scar tissue is forming, shown as fibrous strands. The liver's normal reddish-brown color is replaced with sickly yellows and greens. Toxic particles float around. The {character_name} character's expression is menacing and final. Harsh, unnatural lighting casts deep shadows. The camera does a slow pan across the damaged organ, ending on the character's threatening face."
        ]
        
        # Scene-specific visual environments for benefits
        benefits_visuals = [
            # Scene 1: Nutrient explosion
            f"The scene opens in a vibrant, sun-drenched environment representing health and vitality. The {character_name} character stands center frame with a huge, welcoming smile and sparkling eyes. It's surrounded by animated, glowing symbols of nutrition - vitamins (A, C, D, E) float around as shimmering particles, minerals sparkle like small stars, and protein molecules dance playfully. The character gestures enthusiastically outward. The background features a beautiful gradient of warm colors - oranges, yellows, and soft greens. Sunlight streams from above, creating a magical, wholesome atmosphere. The camera does a gentle orbit around the character. Everything feels alive, energetic and positive.",
            
            # Scene 2: Immune system boost
            f"The scene transitions to show the interior of the human body, but bright and healthy. White blood cells (depicted as cute, energetic warrior-like cells) are shown becoming stronger and more numerous. The {character_name} character appears like a coach or teacher, gesturing encouragingly to the immune cells. Shields with plus signs appear around the cells, representing increased immunity. Germs or viruses (shown as small, harmless-looking creatures) are being easily defeated. The color palette is vibrant blues, whites, and greens suggesting cleanliness and health. Soft, hopeful lighting bathes everything. The character high-fives a white blood cell. The mood is empowering and educational.",
            
            # Scene 3: Strong bones & sharp mind
            f"The scene splits to show both a strong, healthy bone structure and an active, glowing brain. The {character_name} character stands between them, pointing proudly at each. The bones are shown as sturdy, white and dense, with calcium crystals sparkling on their surface. The brain glows with active neural pathways - electrical signals fire rapidly in beautiful patterns of light. Energy flows smoothly. The character does a triumphant pose. The background is a soft, inspiring gradient of purples and blues suggesting wisdom and strength. Warm, encouraging lighting highlights the healthy organs. The camera slowly pulls back to show the character connecting both systems.",
            
            # Scene 4: Healthy heart & longevity
            f"The final scene shows a strong, rhythmically beating heart in perfect health. The {character_name} character stands beside it with a caring, protective gesture. The heart beats steadily and powerfully, glowing with a healthy pinkish-red hue. Blood flows smoothly through clean, clear arteries. A timeline or path stretches into the distance, representing a long, healthy life ahead. The character waves goodbye warmly. The color palette is warm and hopeful - soft pinks, golds, and greens. Golden hour lighting creates a perfect, inspirational atmosphere. The camera slowly zooms out to show the whole healthy body system. The mood is uplifting and motivational."
        ]
        
        # Map voice tone to description and emotion (SAME AS MAIN METHOD)
        voice_map = {
            "male_strong": ("Deep, resonant, strong MALE voice", "angry" if topic_mode == "side_effects" else "confident"),
            "male_friendly": ("Warm, friendly MALE voice", "cheerful"),
            "female_soft": ("Gentle, soothing FEMALE voice", "calm"),
            "female_friendly": ("Friendly, warm FEMALE voice", "happy"),
            "child_happy": ("Cute, playful child voice", "excited"),
            "child_excited": ("Energetic, enthusiastic child voice", "very excited"),
            "cheerful": ("Upbeat, energetic voice", "joyful"),
            "calm": ("Soothing, peaceful voice", "serene"),
            "wise": ("Knowledgeable teacher voice", "confident"),
            "cartoon": ("Silly, animated voice", "playful"),
            "superhero": ("Brave, heroic voice", "confident"),
            "narrator": ("Clear storytelling voice", "neutral")
        }
        
        # Get voice description and emotion based on selected voice_tone
        voice_desc, voice_emotion = voice_map.get(voice_tone, ("Friendly voice", "neutral"))
        
        for i in range(num_scenes):
            scene_num = i + 1
            
            # Use different dialogue for each scene
            dialogue = dialogues[i % len(dialogues)]
            
            # Use scene-specific visual descriptions
            if topic_mode == "side_effects":
                visual_prompt = side_effects_visuals[i % len(side_effects_visuals)]
            else:
                visual_prompt = benefits_visuals[i % len(benefits_visuals)]
            
            complete_prompt = f"""Visual Prompt:
{visual_prompt}

Dialogue ({lang_display}):
{dialogue}

[SCENE METADATA]
Duration: 8 seconds
Aspect Ratio: 9:16

[AUDIO STYLE]
Voice: {voice_desc}. Pitch/Timbre: {voice_tone}. Emotion: {voice_emotion}.
Background: {'Low ominous hum' if topic_mode == 'side_effects' else 'Upbeat background music'}

[LIP SYNC DATA]
0.0s-8.0s
Speaker: {character_lower}
Voice ID: {speaker_id}
Lip Sync Target: {character_lower}_face_mesh
Text: "{dialogue}"
"""
            
            scenes.append({
                "scene_number": scene_num,
                "visual_prompt": visual_prompt,
                "dialogue": dialogue,
                "emotion": voice_emotion,
                "teaching_point": f"{topic_mode.title()} - Part {scene_num}",
                "voice_type": voice_desc,
                "voice_emotion": voice_emotion,
                "background_audio": "Low ominous hum" if topic_mode == "side_effects" else "Upbeat background music",
                "speaker_id": speaker_id,
                "prompt": complete_prompt
            })
        
        return {
            "scenes": scenes,
            "total_scenes": num_scenes,
            "character_name": character_name,
            "topic": f"{character_name} - {topic_mode}"
        }

# Create global instance
character_dialogue_generator = CharacterDialogueGenerator()
