# Educational Character - Distributed Appearance Feature

## Overview
Educational videos now feature **distributed character appearances** where the educator appears briefly multiple times throughout the video (4-5 seconds total) while the rest of the time shows educational visual illustrations.

## Feature Specifications

### Scene Distribution Pattern

For a **60-second educational video**:
- **Total Scenes**: ~8 scenes (8-second duration)
- **CHARACTER Scenes**: **3 scenes** (Start, Middle, End)
  - Duration: 8 seconds (Full scene)
  - Positions: First, Middle, Last scene
  - Purpose: Introduction, Key Emphasis, Conclusion/Pitch
- **VISUAL Scenes**: ~5 scenes (filling the gaps)
  - Duration: 8 seconds
  - Purpose: Illustrations acting as B-roll between character segments

### Scene Types

#### TYPE A - CHARACTER (ON-SCREEN)
- **Duration**: 8 seconds (Full scene)
- **Dialogue**: 25-30 words (complete thought)
- **Visual**: Educator on camera, engaging directly
- **Positions**: Start, Middle, End
- **Metadata**: `scene_type: CHARACTER (ON-SCREEN)`

#### TYPE B - CHARACTER (OFF-SCREEN)
- **Duration**: 8 seconds
- **Dialogue**: 25-30 words (CONTINUOUS SPEECH - NO NARRATION)
- **Visual**: Detailed illustrations. **Same speaker** continues talking off-screen.
- **Positions**: Scenes between anchors
- **Metadata**: `scene_type: CHARACTER (OFF-SCREEN)`

### Distribution Pattern

```
8-scene example:
1. ON-SCREEN (Intro)
2. OFF-SCREEN (Visuals + Continuous Speech)
3. OFF-SCREEN (Visuals + Continuous Speech)
4. ON-SCREEN (Key Emphasis)
5. OFF-SCREEN (Visuals + Continuous Speech)
...
8. ON-SCREEN (Conclusion)
```

### Audio Settings & Voice Continuity (STRICT)

**CRITICAL REQUIREMENT**: The caller's natural microphone voice must be used consistently.

#### Audio Configuration Block
Every scene includes this strict configuration:

```
=== AUDIO SETTINGS (STRICT – DO NOT OVERRIDE) ===
Input Source: Caller Microphone (Primary)
Voice Capture: Live caller mic only
Audio Mode: Continuous speech from same speaker as Scene 1
No synthetic TTS
No default narration
No voice replacement
```

#### Voice Continuity Lock

✅ **Identity Lock**: Speaker identity is unchanged from Scene 1  
✅ **Seamless Audio**: Same human voice continues even when off-screen  
✅ **Continuous Explanation**: Audio is part of a single continuous talk, not separate narration clips  
✅ **No AI Voice**: AI-generated narration is STRICTLY DISABLED  

**Key Point**: Whether the scene is ON-SCREEN or OFF-SCREEN, it is the **same person** speaking into the **same microphone** continuously.

#### Why This Matters

- **Professional quality** - Consistent voice = professional production value
- **Learning experience** - Students connect with one consistent instructor voice
- **Authenticity** - Real human voice builds trust and engagement
- **Seamless flow** - Voice-over feels natural, not robotic or disconnected

## Implementation Details

### Backend Changes

#### 1. Scene Calculation (`educational_character_service.py`)

```python
# Calculate distributed scene pattern
num_total_scenes = max(1, total_duration // 8)
num_character_scenes = max(2, min(5, total_duration // 15))  # 4-5 for 60s
num_visual_scenes = num_total_scenes - num_character_scenes
```

#### 2. AI Prompt Generation

The system now instructs Gemini to create two distinct scene types:

**CHARACTER Scene Template:**
```
===SCENE X (TYPE: CHARACTER)===
Visual Prompt:
[Character name], professional appearance, engaging directly with camera...

Dialogue (HINDI):
[10-12 words max]

Teaching Point:
[Brief introduction]
===END SCENE X===
```

**VISUAL Scene Template:**
```
===SCENE X (TYPE: VISUAL)===
Visual Prompt:
Detailed 3D diagram showing [concept]... [150+ word description]

Dialogue (HINDI):
[18-22 words of voiceover narration]

Teaching Point:
[Detailed explanation]
===END SCENE X===
```

#### 3. Scene Parsing

The parser now:
- Detects scene type from `(TYPE: CHARACTER/VISUAL)` marker
- Assigns appropriate duration (2s or 7s)
- Adds scene type metadata to each scene
- Tracks and reports character vs visual scene counts

### Example Output

For teaching "AI Video Generation" (60 seconds):

**Scene 1 (CHARACTER - 2s):**
- Visual: Teacher on camera, welcoming smile
- Dialogue: "आज मैं आपको AI के बारे में बताऊँगा।"
- Teaching: Introduction

**Scene 2 (VISUAL - 7s):**
- Visual: 3D neural network diagram with flowing data
- Dialogue: "AI models में data से patterns सीखते हैं और फिर नए situations में apply करते हैं।"
- Teaching: How AI learns

**Scene 3 (VISUAL - 7s):**
- Visual: Split-screen comparison (traditional vs AI)
- Dialogue: "Traditional methods में hours लगते हैं जबकि AI seconds में काम complete कर देता है।"
- Teaching: AI efficiency

**Scene 4 (CHARACTER - 2s):**
- Visual: Teacher gesturing, explaining
- Dialogue: "अब देखते हैं कि यह कैसे काम करता है।"
- Teaching: Transition

## Benefits

### Educational Value
✅ **Better retention** - Visual illustrations reinforce concepts
✅ **Clearer explanations** - Separate visual time from teacher time
✅ **Professional appearance** - Mix of talking-head and content

### Engagement
✅ **Dynamic pacing** - Alternating between character and visuals
✅ **Visual variety** - Prevents monotony of constant talking head
✅ **Focused learning** - Visuals illustrate while voice explains

### Production Quality
✅ **Realistic distribution** - Mimics professional educational videos
✅ **Flexible duration** - Works for any video length
✅ **AI-generated visuals** - System creates appropriate illustrations

## Usage

When creating an educational character video:

1. **Set content type** to "educational"
2. **Specify teaching topic** in scenario field
3. **Choose total duration** (e.g., 60 seconds)
4. **System automatically**:
   - Calculates optimal scene distribution
   - Creates CHARACTER scenes (brief appearances)
   - Creates VISUAL scenes (teaching illustrations)
   - Generates appropriate dialogue for each type

## Technical Notes

- Scene type detection uses regex: `r'\(TYPE:\s*(CHARACTER|VISUAL)\)'`
- CHARACTER scenes: 2 seconds, max 10-12 words
- VISUAL scenes: 7 seconds, max 18-22 words
- Voice description remains consistent across all scenes
- All scenes include proper metadata for frontend rendering
