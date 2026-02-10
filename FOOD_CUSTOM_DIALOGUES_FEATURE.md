# Custom Dialogues Feature for Food Character

## Implementation Complete! ✅

Users can now provide their own custom dialogues for food characters, and Gemini will automatically break them into scene-wise prompts.

## How It Works

### Two Modes

#### Mode 1: Custom Dialogues (NEW)
- **User provides dialogues** in the textbox
- **Gemini breaks them** into scenes automatically
- Each scene gets 7-8 seconds of dialogue
- Visual prompts are generated based on character and tone

#### Mode 2: Auto-Generate (Existing)
- **User leaves textbox empty**
- **Gemini generates** both dialogues and visuals
- Based on character name and topic (benefits/side effects)

## User Interface

### New Textbox Added
Location: Between "Scenario" and "Visual Style" fields

**Features:**
- 💬 Label: "Custom Dialogues (Optional)"
- Placeholder with example in Devanagari + English format
- Character count feedback
- Shows how many scenes dialogues will be broken into
- Highlighted in green when dialogues provided

**Example Placeholder:**
```
Enter your own dialogues here, and AI will break them into scenes.

Example:
मैं Apple हूँ। मुझमें Vitamin C है। Heart को healthy रखता हूँ। Energy boost करता हूँ।

Leave empty if you want AI to generate dialogues automatically.
```

## Backend Processing

### When Custom Dialogues Provided:

1. **Receives user dialogues** from frontend
2. **Gemini prompt changes** to "break these dialogues" mode
3. **Splits dialogues evenly** across calculated number of scenes
4. **Preserves exact dialogues** (doesn't translate or modify)
5. **Generates visual prompts** for each portion
6. **Infers teaching points** from each dialogue segment

### When Empty (Auto-Generate):

Uses the existing behavior - Gemini creates both dialogues and visuals based on character and topic.

## Example Usage

### Input (Custom Dialogues Mode):
```
Character: Apple
Topic: Benefits
Duration: 16 seconds (2 scenes)
Language: Hindi
Custom Dialogues: "मैं Apple हूँ। मुझमें Vitamin C है। Heart को healthy रखता हूँ। Energy boost करता हूँ।"
```

### Output:
```
Scene 1 (8 seconds):
Dialogue: "मैं Apple हूँ। मुझमें Vitamin C है।"
Visual: Anthropomorphic Apple character, 3D Pixar style, vibrant red...
Teaching Point: Apples contain Vitamin C

Scene 2 (8 seconds):
Dialogue: "Heart को healthy रखता हूँ। Energy boost करता हूँ।"
Visual: Same cheerful Apple, pointing at heart icon...
Teaching Point: Good for heart health and energy
```

## Modified Files

### Frontend
**File**: `Frontend/src/pages/CharacterPage.jsx`
- Line 50: Added `customDialogues` state
- Line 120: Send `custom_dialogues` to API
- Lines 274-292: New textbox UI with feedback

### Backend Models
**File**: `backend/app/character/models.py`
- Line 17: Added `custom_dialogues` field to CharacterSceneRequest

### Backend Routes
**File**: `backend/app/character/routes.py`
- Line 44: Pass `custom_dialogues` to service

### Backend Service Dispatcher
**File**: `backend/app/character/service.py`
- Line 146: Added `custom_dialogues` parameter
- Line 168: Pass to food_character_generator

### Backend Food Service
**File**: `backend/app/character/food_character_service.py`
- Line 34: Added `custom_dialogues` parameter
- Lines 68-105: Conditional prompt logic
  - Lines 71-105: Custom dialogues mode prompt
  - Lines 106+: Auto-generate mode prompt (existing)

## Features

### Custom Dialogues Mode:
✅ User provides exact dialogues they want
✅ Gemini breaks them into equal scenes
✅ Dialogues preserved exactly (no translation)
✅ Visual prompts generated automatically
✅ Teaching points inferred from dialogues
✅ Respects 7-second scene limits

### Auto-Generate Mode (Existing):
✅ Gemini creates full content
✅ Based on character + topic
✅ Benefits or side effects
✅ Devanagari + English format

## Validation

### Frontend:
- Shows green check when dialogues provided
- Displays scene count based on duration
- Helpful placeholder examples

### Backend:
- Splits dialogues evenly across scenes
- Enforces word limits (20 words scene 1, 15 words others)
- Maintains visual quality (80+ words per visual prompt)

## Benefits

1. **Flexibility**: Users can provide exact dialogues they need
2. **Control**: Full control over what character says
3. **Efficiency**: AI handles visual prompts and scene breaking
4. **Consistency**: Dialogues stay exactly as user wrote them
5. **Easy**: Simple textbox, optional feature

## Testing

### Test Case 1: Custom Dialogues
**Input:**
```
Character: Carrot
Duration: 16 seconds
Custom Dialogues: "मैं Carrot हूँ। Vision को improve करता हूँ। Vitamin A भरपूर है मुझमें।"
```

**Expected:**
- 2 scenes (16 seconds ÷ 8)
- Scene 1: "मैं Carrot हूँ। Vision को improve करता हूँ।"
- Scene 2: "Vitamin A भरपूर है मुझमें।"

### Test Case 2: Auto-Generate
**Input:**
```
Character: Banana
Duration: 8 seconds
Custom Dialogues: (empty)
```

**Expected:**
- 1 scene
- Gemini generates: "मैं Banana हूँ। Energy boost करता हूँ।"

## Summary

**Custom Dialogues Feature:**
- ✅ Frontend textbox with examples and feedback
- ✅ Backend handles both custom and auto-generate modes
- ✅ Gemini breaks custom dialogues into scenes
- ✅ Preserves exact user dialogues
- ✅ Generates visual prompts automatically
- ✅ Optional - works alongside existing auto-generate

**Users now have complete control over food character dialogues! 🍎🥕🍌**
