# Custom Voice Tone Feature - Educational Character

## Overview
This feature allows users to describe their own custom voice characteristics when generating educational character videos, instead of being limited to predefined voice options.

## How It Works

### Frontend (User Experience)

1. **Voice Selection Dropdown**
   - First option: "✍️ I will describe" (value: "custom")
   - When selected, a custom voice description textbox appears

2. **Custom Voice Description Textbox**
   - Purple-highlighted box with helpful placeholder examples
   - Minimum 20 characters required for quality
   - Character counter to guide users
   - Warning shown if description is too short
   - Examples provided in placeholder

3. **Validation**
   - Generate button is disabled if:
     - Character name is empty
     - Custom voice is selected but description < 20 characters

### Backend (Processing)

1. **API Request**
   - Endpoint: `/gemini/generate-character-dialogue`
   - When `voice_tone` = "custom", the `custom_voice_description` field is sent

2. **Voice Prompt Generation**
   - Method: `_create_custom_voice_prompt()`
   - Converts user description into TTS-friendly format
   - Format: "{user_description}. Clean audio, professional recording quality."

3. **Scene Generation**
   - Custom voice description is used for ALL scenes in the video
   - Stored in the SPEAKER section of each scene prompt
   - Ensures consistency across all generated scenes

## Example Usage

### User Input (Custom Voice Description):
```
Deep authoritative male voice with clear pronunciation, moderate pace around 150 WPM, 
neutral Indian accent, professional and confident tone, warm and engaging delivery
```

### Backend Processing:
```python
# Detected: voice_tone == "custom"
master_voice_description = _create_custom_voice_prompt(custom_voice_description)
# Result: "Deep authoritative male voice with clear pronunciation, moderate pace around 150 WPM, neutral Indian accent, professional and confident tone, warm and engaging delivery. Clean audio, professional recording quality."
```

### Final Scene Output:
```
===== SCENE 1 (7 SECONDS) =====

VISUAL (VEO 3):
Yagnesh Modh, Realistic Character style, brightly lit modern digital studio...

DIALOGUE (HINDI):
Aaj main bataunga AI videos kaise bante hain.

TEACHING:
Introduction to AI video generation

=== METADATA ===
Duration: 7-8 seconds (SHORT!)
Style: Realistic Character
Type: educational

SPEAKER:
ID: yagnesh_modh_custom
Voice: Deep authoritative male voice with clear pronunciation, moderate pace around 150 WPM, neutral Indian accent, professional and confident tone, warm and engaging delivery. Clean audio, professional recording quality.
Text: "Aaj main bataunga AI videos kaise bante hain."
```

## Implementation Files

### Frontend
- **File**: `Frontend/src/pages/EducationalCharacterPage.jsx`
- **Key Components**:
  - Lines 9: Custom voice option in VOICE_TONES array
  - Lines 46: customVoiceDescription state variable
  - Lines 256-278: Conditional custom voice textbox UI
  - Lines 128-130: API request with custom_voice_description

### Backend
- **File**: `backend/app/character/educational_character_service.py`
- **Key Methods**:
  - Lines 145-154: `generate_dialogue()` - accepts custom_voice_description parameter
  - Lines 174-190: Custom voice detection and processing logic
  - Lines 423-436: `_create_custom_voice_prompt()` - converts user input to voice prompt

- **File**: `backend/app/character/models.py`
  - Line 11: `custom_voice_description` field in CharacterSceneRequest model

- **File**: `backend/app/character/routes.py`
  - Line 38: Passes custom_voice_description to service

- **File**: `backend/app/character/service.py`
  - Line 140: Accepts custom_voice_description parameter
  - Line 173: Passes to educational_character_generator

## Features

✅ **Implemented**
- Custom voice option in dropdown
- Dynamic textbox appearance
- Character counter
- Validation (minimum 20 chars)
- API integration
- Voice prompt generation
- Consistent voice across all scenes

✅ **Enhancements Added**
- Better placeholder examples (male/female examples)
- Character counter
- Short description warning
- Improved UI with purple highlighting
- Fade-in animation
- Button validation

## Testing

To test this feature:

1. Navigate to Educational Character page
2. Select "✍️ I will describe" from Voice Tone dropdown
3. Enter a custom voice description (e.g., "Deep male voice, professional tone")
4. Fill in other required fields (character name, teaching topic)
5. Click "Generate Teaching Scenes"
6. Verify the generated scenes use your custom voice description

## Notes

- Minimum 20 characters required for quality voice descriptions
- Custom voice description is used for ALL scenes to maintain consistency
- Format is optimized for TTS systems
- Falls back to "male_friendly" if custom selected but no description provided
